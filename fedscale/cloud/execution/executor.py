# -*- coding: utf-8 -*-
import collections
import gc
import pickle
import random
import time
from argparse import Namespace
import copy

import numpy as np
import torch
import wandb
import grpc
import logging

import fedscale.cloud.channels.job_api_pb2 as job_api_pb2
import fedscale.cloud.logger.executor_logging as logger
from fedscale.cloud.channels.channel_context import ClientConnections
from fedscale.cloud.execution.tensorflow_client import TensorflowClient
from fedscale.cloud.execution.torch_client import TorchClient
from fedscale.cloud.execution.data_processor import collate, voice_collate_fn
from fedscale.cloud.execution.rl_client import RLClient
from fedscale.cloud.fllibs import *
from fedscale.dataloaders.divide_data import DataPartitioner, select_dataset
import gzip

class Executor(object):
    """Abstract class for FedScale executor.

    Args:
        args (dictionary): Variable arguments for fedscale runtime config. defaults to the setup in arg_parser.py

    """

    def __init__(self, args):
        # initiate the executor log path, and executor ips
        logger.initiate_client_setting()

        self.model_adapter = self.get_client_trainer(args).get_model_adapter(
            init_model()
        )

        self.args = args
        self.num_executors = args.num_executors
        # ======== env information ========
        self.this_rank = args.this_rank
        self.executor_id = str(self.this_rank)


        # === 2) grab the very first global weights
        #     (deepcopy because we’ll mutate local_weights in‐place)
        self.global_weights = copy.deepcopy(self.model_adapter.get_weights())
        self.local_weights  = copy.deepcopy(self.global_weights)
        self.alpha = 0.5


        # ======== model and data ========
        self.training_sets = self.test_dataset = None

        # ======== channels ========
        self.aggregator_communicator = ClientConnections(args.ps_ip, args.ps_port)

        # ======== runtime information ========
        self.collate_fn = None
        self.round = 0
        self.start_run_time = time.time()
        self.received_stop_request = False
        self.event_queue = collections.deque()

        if args.wandb_token != "":
            os.environ["WANDB_API_KEY"] = args.wandb_token
            self.wandb = wandb
            if self.wandb.run is None:
                self.wandb.init(
                    project=f"fedscale-{args.job_name}",
                    name=f"executor{args.this_rank}-{args.time_stamp}",
                    group=f"{args.time_stamp}",
                )
            else:
                logging.error("Warning: wandb has already been initialized")

        else:
            self.wandb = None
        super(Executor, self).__init__()

    def setup_env(self):
        """Set up experiments environment"""
        logging.info(f"(EXECUTOR:{self.this_rank}) is setting up environ ...")
        self.setup_seed(seed=1)

    def setup_communication(self):
        """Set up grpc connection"""
        self.init_control_communication()
        self.init_data_communication()

    def setup_seed(self, seed=1):
        """Set random seed for reproducibility

        Args:
            seed (int): random seed

        """
        torch.manual_seed(seed)
        torch.backends.cudnn.deterministic = True
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        random.seed(seed)

    def init_control_communication(self):
        """Create communication channel between coordinator and executor.
        This channel serves control messages.
        """
        self.aggregator_communicator.connect_to_server()

    def init_data_communication(self):
        """In charge of jumbo data traffics (e.g., fetch training result)"""
        pass

    def init_data(self):
        """Return the training and testing dataset

        Returns:
            Tuple of DataPartitioner class: The partioned dataset class for training and testing

        """
        train_dataset, test_dataset = init_dataset()
        if self.args.task == "rl":
            return train_dataset, test_dataset
        if self.args.task == "nlp":
            self.collate_fn = collate
        elif self.args.task == "voice":
            self.collate_fn = voice_collate_fn
        # load data partitionxr (entire_train_data)
        logging.info("Data partitioner starts ...")

        training_sets = DataPartitioner(
            data=train_dataset, args=self.args, numOfClass=self.args.num_class
        )
        training_sets.partition_data_helper(
            num_clients=self.args.num_participants,
            data_map_file=self.args.data_map_file,
        )

        testing_sets = DataPartitioner(
            data=test_dataset,
            args=self.args,
            numOfClass=self.args.num_class,
            isTest=True,
        )
        testing_sets.partition_data_helper(num_clients=self.num_executors)

        logging.info("Data partitioner completes ...")

        return training_sets, testing_sets

    def run(self):
        """Start running the executor by setting up execution and communication environment, and monitoring the grpc message."""
        self.setup_env()
        self.training_sets, self.testing_sets = self.init_data()
        self.setup_communication()
        self.event_monitor()

    def dispatch_worker_events(self, request):
        """Add new events to worker queues

        Args:
            request (string): Add grpc request from server (e.g. MODEL_TEST, MODEL_TRAIN) to event_queue.

        """
        self.event_queue.append(request)

    def deserialize_response(self, responses):
        """Deserialize the response from server

        Args:
            responses (byte stream): Serialized response from server.

        Returns:
            ServerResponse defined at job_api.proto: The deserialized response object from server.

        """
        # return pickle.loads(responses)
        raw = gzip.decompress(responses)
        return pickle.loads(raw)


    def serialize_response(self, responses):
        """Serialize the response to send to server upon assigned job completion

        Args:
            responses (string, bool, or bytes): TorchClient responses after job completion.

        Returns:
            bytes stream: The serialized response object to server.

        """
        # return pickle.dumps(responses)
        raw = pickle.dumps(responses)
        return gzip.compress(raw)

    def UpdateModel(self, model_weights):
        """Receive the broadcasted global model for current round

        Args:
            config (PyTorch or TensorFlow model): The broadcasted global model config

        """
        self.round += 1
        self.model_adapter.set_weights(model_weights, is_aggregator=False)

    def Train(self, config):
        """Load train config and data to start training on that client

        Args:
            config (dictionary): The client training config.

        Returns:
            tuple (int, dictionary): The client id and train result

        """
        client_id, train_config = config["client_id"], config["task_config"]

        if "model" not in config or not config["model"]:
            raise "The 'model' object must be a non-null value in the training config."
        
        # 1) pull the server's broadcast into self.global_weights
        global_blob = config["model"]
        self.global_weights = global_blob


        # 1. Evaluate both local and global performance
        local_acc = self.evaluate_model(self.local_weights)
        global_acc = self.evaluate_model(self.global_weights)

        # 2. Adjust alpha if local outperforms global significantly
        threshold = 0.02  # tunable hyperparameter
        if local_acc - global_acc > threshold:
            self.alpha = min(self.alpha + 0.1, 1.0)
        elif global_acc - local_acc > threshold:
            self.alpha = max(self.alpha - 0.1, 0.0)

        logging.info(f"[Executor:{self.executor_id}] Adjusted α = {self.alpha:.2f}")


        # 2) mix local + global via α
        mixed = [
            self.alpha * lw + (1 - self.alpha) * gw
            for lw, gw in zip(self.local_weights, self.global_weights)
        ]
        # set that as the model you actually train
        self.model_adapter.set_weights(mixed, is_aggregator=False)



        client_conf = self.override_conf(train_config)
        train_res = self.training_handler(
            client_id=client_id, conf=client_conf, model=mixed
        )

        self.local_weights = self.model_adapter.get_weights()
        

        if not isinstance(train_res, dict):
            temp_train_res = {}
            train_res = temp_train_res

        train_res['client_eval_local_acc'] = local_acc   # local_acc was calculated earlier in Train
        train_res['client_eval_global_acc'] = global_acc # global_acc was calculated earlier in Train
        train_res['client_alpha'] = self.alpha          # self.alpha was calculated earlier in Train

        logging.info(f"Got local weights of size {len(pickle.dumps(self.local_weights))/1e6:.2f} MB")

        try:
            logging.info("About to call CLIENT_EXECUTE_COMPLETION...")
            # Report execution completion meta information
            response = self.aggregator_communicator.stub.CLIENT_EXECUTE_COMPLETION(
                job_api_pb2.CompleteRequest(
                    client_id=str(client_id),
                    executor_id=self.executor_id,
                    event=commons.CLIENT_TRAIN,
                    status=True,
                    msg=None,
                    meta_result=None,
                    data_result=None,
                )
            )
            self.dispatch_worker_events(response)

        except grpc.RpcError as e:
            logging.error(f"gRPC error details:")
            logging.error(f"  Error code: {e.code()}")
            logging.error(f"  Error details: {e.details()}")
            logging.error(f"  Error debug string: {e.debug_error_string()}")
            if hasattr(e, 'initial_metadata'):
                logging.error(f"  Initial metadata: {e.initial_metadata()}")
            if hasattr(e, 'trailing_metadata'):
                logging.error(f"  Trailing metadata: {e.trailing_metadata()}")
            
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                logging.error("Aggregator went away—reconnecting or exiting")
            elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
                logging.error("gRPC message size limit exceeded")
            else:
                logging.error(f"Unexpected gRPC error: {e}")


        return client_id, train_res


    def evaluate_model(self, weights):
        """Evaluate given weights on local test set and return accuracy or loss."""
        self.model_adapter.set_weights(weights, is_aggregator=False)
        test_config = self.override_conf({
            "rank": self.this_rank,
            "tokenizer": tokenizer,
        })
        client = self.get_client_trainer(test_config)
        data_loader = select_dataset(
            self.this_rank,
            self.testing_sets,
            batch_size=self.args.test_bsz,
            args=self.args,
            isTest=True,
            collate_fn=self.collate_fn,
        )
        res = client.test(data_loader, model=self.model_adapter.get_model(), conf=test_config)
        return res["top_1"] / res["test_len"]  # or use res["test_loss"] / res["test_len"]



    def Test(self, config):
        """Model Testing. By default, we test the accuracy on all data of clients in the test group

        Args:
            config (dictionary): The client testing config.

        """
        test_res = self.testing_handler(model=config["model"])
        test_res = {"executorId": self.this_rank, "results": test_res}

        # Report execution completion information
        response = self.aggregator_communicator.stub.CLIENT_EXECUTE_COMPLETION(
            job_api_pb2.CompleteRequest(
                client_id=self.executor_id,
                executor_id=self.executor_id,
                event=commons.MODEL_TEST,
                status=True,
                msg=None,
                meta_result=None,
                data_result=self.serialize_response(test_res),
            )
        )
        self.dispatch_worker_events(response)

    def Stop(self):
        """Stop the current executor"""
        logging.info(f"Terminating the executor ...")
        self.aggregator_communicator.close_sever_connection()
        self.received_stop_request = True
        if self.wandb != None:
            self.wandb.finish()

    def report_executor_info_handler(self):
        """Return the statistics of training dataset

        Returns:
            int: Return the statistics of training dataset, in simulation return the number of clients

        """
        return self.training_sets.getSize()

    def override_conf(self, config):
        """Override the variable arguments for different client

        Args:
            config (dictionary): The client runtime config.

        Returns:
            dictionary: Variable arguments for client runtime config.

        """
        default_conf = vars(self.args).copy()

        for key in config:
            default_conf[key] = config[key]

        return Namespace(**default_conf)

    def get_client_trainer(self, conf):
        """
        Returns a framework-specific client that handles training and evaluation.
        :param conf: job config
        :return: framework-specific client instance
        """
        if conf.engine == commons.TENSORFLOW:
            return TensorflowClient(conf)
        elif conf.engine == commons.PYTORCH:
            if conf.task == "rl":
                return RLClient(conf)
            else:
                return TorchClient(conf)
        raise Exception("Currently, FedScale supports tensorflow and pytorch.")

    def training_handler(self, client_id, conf, model):
        """Train model given client id

        Args:
            client_id (int): The client id.
            conf (dictionary): The client runtime config.

        Returns:
            dictionary: The train result

        """
        self.model_adapter.set_weights(model, is_aggregator=False)
        conf.client_id = client_id
        conf.tokenizer = tokenizer
        client_data = (
            self.training_sets
            if self.args.task == "rl"
            else select_dataset(
                client_id,
                self.training_sets,
                batch_size=conf.batch_size,
                args=self.args,
                collate_fn=self.collate_fn,
            )
        )
        client = self.get_client_trainer(self.args)
        train_res = client.train(
            client_data=client_data, model=self.model_adapter.get_model(), conf=conf
        )
        print(f"loss curve from train_res for client: is {train_res['loss_curve']}")
        # logging.info(f"train_res for client: is {train_res}")
        return train_res

    def testing_handler(self, model):
        """Test model

        Args:
            args (dictionary): Variable arguments for fedscale runtime config. defaults to the setup in arg_parser.py
            config (dictionary): Variable arguments from coordinator.
        Returns:
            dictionary: The test result

        """
        self.model_adapter.set_weights(model, is_aggregator=False)
        test_config = self.override_conf(
            {
                "rank": self.this_rank,
                "memory_capacity": self.args.memory_capacity,
                "tokenizer": tokenizer,
            }
        )
        client = self.get_client_trainer(test_config)
        data_loader = select_dataset(
            self.this_rank,
            self.testing_sets,
            batch_size=self.args.test_bsz,
            args=self.args,
            isTest=True,
            collate_fn=self.collate_fn,
        )

        test_results = client.test(
            data_loader, model=self.model_adapter.get_model(), conf=test_config
        )
        self.log_test_result(test_results)
        gc.collect()

        return test_results

    def client_register(self):
        """Register the executor information to the aggregator"""
        start_time = time.time()
        while time.time() - start_time < 180:
            try:
                response = self.aggregator_communicator.stub.CLIENT_REGISTER(
                    job_api_pb2.RegisterRequest(
                        client_id=self.executor_id,
                        executor_id=self.executor_id,
                        executor_info=self.serialize_response(
                            self.report_executor_info_handler()
                        ),
                    )
                )
                self.dispatch_worker_events(response)
                break
            except Exception as e:
                logging.warning(
                    f"Failed to connect to aggregator {e}. Will retry in 5 sec."
                )
                time.sleep(5)

    def client_ping(self):
        """Ping the aggregator for new task"""
        try:
            print(f"[Executor] calling CLIENT_PING…")
            response = self.aggregator_communicator.stub.CLIENT_PING(
                job_api_pb2.PingRequest(
                    client_id=self.executor_id, executor_id=self.executor_id
                )
            )
            # after we get a raw ServerResponse proto…
            logging.debug(f"[Executor] CLIENT_PING ← event={response.event!r} "
                        f"meta={len(response.meta)} bytes data={len(response.data)} bytes")
        
            self.dispatch_worker_events(response)
        except Exception:
            logging.exception("🔴 CLIENT_PING failed")
            raise

    # def event_monitor(self):
    #     """Activate event handler once receiving new message"""
    #     logging.info("Start monitoring events ...")
    #     self.client_register()

    #     while not self.received_stop_request:
    #         if len(self.event_queue) > 0:
    #             request = self.event_queue.popleft()
    #             current_event = request.event

    #             if current_event == commons.CLIENT_TRAIN:
    #                 train_config = self.deserialize_response(request.meta)
    #                 train_model = self.deserialize_response(request.data)
    #                 train_config["model"] = train_model
    #                 train_config["client_id"] = int(train_config["client_id"])
    #                 client_id, train_res = self.Train(train_config)

    #                 # Upload model updates
    #                 future_call = self.aggregator_communicator.stub.CLIENT_EXECUTE_COMPLETION.future(
    #                     job_api_pb2.CompleteRequest(
    #                         client_id=str(client_id),
    #                         executor_id=self.executor_id,
    #                         event=commons.UPLOAD_MODEL,
    #                         status=True,
    #                         msg=None,
    #                         meta_result=None,
    #                         data_result=self.serialize_response(train_res),
    #                     )
    #                 )
    #                 future_call.add_done_callback(
    #                     lambda _response: self.dispatch_worker_events(
    #                         _response.result()
    #                     )
    #                 )

    #             elif current_event == commons.MODEL_TEST:
    #                 # test_config = self.deserialize_response(request.meta)
    #                 # test_model = self.deserialize_response(request.data)
    #                 test_config = self.deserialize_response(request.meta)
    #                 test_config["model"]   = self.global_weights
    #                 test_config["client_id"] = int(test_config["client_id"])
    #                 self.Test(test_config)

    #             elif current_event == commons.UPDATE_MODEL:
    #                 # model_weights = self.deserialize_response(request.data)
    #                 # self.UpdateModel(model_weights)   

    #                 stream = self.aggregator_communicator.stub.StreamUpdateModel(
    #                     job_api_pb2.PingRequest(
    #                         client_id   = self.executor_id,
    #                         executor_id = self.executor_id
    #                     )
    #                 )
    #                 compressed = b"".join(chunk.payload for chunk in stream)
    #                 # Decompress & deserialize
    #                 raw = gzip.decompress(compressed)
    #                 model_weights = pickle.loads(raw)
    #                 self.UpdateModel(model_weights)

    #             elif current_event == commons.SHUT_DOWN:
    #                 self.Stop()
    #                 break

    #             elif current_event == commons.DUMMY_EVENT:
    #                 pass
    #         else:
    #             time.sleep(1)
    #             try:
    #                 self.client_ping()
    #             except Exception as e:
    #                 logging.info(
    #                     f"Caught exception {e} from aggregator, terminating executor {self.this_rank} ..."
    #                 )
    #                 self.Stop()


    def event_monitor(self):
        """Activate event handler once receiving new message"""
        logging.info("Start monitoring events …")
        # 1) Register with the aggregator
        self.client_register()

        # Pre-build a PingRequest so we don't repeatedly construct it
        ping_req = job_api_pb2.PingRequest(
            client_id   = self.executor_id,
            executor_id = self.executor_id,
        )

        while True:
            try:
                # If shutdown was requested inside Train/Test/etc, break
                if self.received_stop_request:
                    break

                # 2) Handle any queued ServerResponse events
                if self.event_queue:
                    request = self.event_queue.popleft()
                    current_event = request.event

                    if current_event == commons.CLIENT_TRAIN:
                        cfg = self.deserialize_response(request.meta)
                        model_blob = self.deserialize_response(request.data)
                        cfg["model"]     = model_blob
                        cfg["client_id"] = int(cfg["client_id"])
                        client_id, train_res = self.Train(cfg)

                        raw_payload = self.serialize_response(train_res)
                        logging.info(f"[Executor:{self.executor_id}] Will upload train_res payload of {len(raw_payload)/1e6:.2f} MB")
                        # upload asynchronously
                        # future = self.aggregator_communicator.stub.CLIENT_EXECUTE_COMPLETION.future(
                        #     job_api_pb2.CompleteRequest(
                        #         client_id    = str(client_id),
                        #         executor_id  = self.executor_id,
                        #         event        = commons.UPLOAD_MODEL,
                        #         status       = True,
                        #         meta_result  = None,
                        #         data_result  = raw_payload,

                        #     )
                        # )
                        

                        ratio = cfg.get("compression", 1.0)   # comes from get_client_conf
                        logging.info(f"[Executor:{self.executor_id}] using compression={ratio}")
                        print(f"[Executor:{self.executor_id}] using compression={ratio}")
                        # update = train_res["update_weight"]   # dict of numpy arrays/tensors
                        update = list(train_res["update_weight"].values())

                        # simple top-k thresholding example:
                        flat = np.concatenate([w.flatten() for w in update])
                        k = int(ratio * flat.size)
                        thresh = np.partition(np.abs(flat), -k)[-k]
                        sparse_update = [w * (np.abs(w) >= thresh) for w in update]


                        nonzeros = sum(np.count_nonzero(w) for w in sparse_update)
                        total    = sum(w.size for w in sparse_update)
                        logging.info(f"[Executor:{self.executor_id}] sparse update is {nonzeros}/{total} nonzeros")
                        print(f"[Executor:{self.executor_id}] sparse update is {nonzeros}/{total} nonzeros")



                        train_res["update_weight"] = sparse_update



                        # future.add_done_callback(lambda f: self.dispatch_worker_events(f.result()))
                        raw      = pickle.dumps(train_res)
                        compressed = gzip.compress(raw)
                        chunk_size = 1 << 20
                        def chunker():
                            for offset in range(0, len(compressed), chunk_size):
                                yield job_api_pb2.ModelChunk(
                                    payload = compressed[offset:offset+chunk_size],
                                    seq_num = offset // chunk_size
                                )
                        ack = self.aggregator_communicator.stub.UploadModel(chunker())
                        logging.info(f"[Executor:{self.executor_id}] UploadModel RPC completed.")
                        print(f"[Executor:{self.executor_id}] UploadModel RPC completed.")
                        fake_resp = job_api_pb2.ServerResponse(event=commons.DUMMY_EVENT, meta=b'', data=b'')
                        self.dispatch_worker_events(fake_resp)
                        # future.add_done_callback(
                        #     lambda resp: logging.info(f"[Executor:{self.executor_id}] UploadModel RPC completed: event={resp.result().event!r}")
                        # )

                    elif current_event == commons.MODEL_TEST:
                        cfg = self.deserialize_response(request.meta)
                        cfg["model"]     = self.global_weights
                        cfg["client_id"] = int(cfg["client_id"])
                        self.Test(cfg)

                    elif current_event == commons.UPDATE_MODEL:
                        # stream in new global weights
                        stream = self.aggregator_communicator.stub.StreamUpdateModel(ping_req)
                        compressed = b"".join(chunk.payload for chunk in stream)
                        raw = gzip.decompress(compressed)
                        weights = pickle.loads(raw)
                        self.UpdateModel(weights)

                    elif current_event == commons.SHUT_DOWN:
                        logging.info("Received SHUT_DOWN from server; stopping executor.")
                        print("Received SHUT_DOWN from server; stopping executor.")
                        break

                    # DUMMY_EVENT → nothing to do
                    # elif current_event == commons.DUMMY_EVENT:
                    #     pass

                else:
                    # 3) No events queued → poll the server
                    time.sleep(1)
                    resp = self.aggregator_communicator.stub.CLIENT_PING(ping_req)
                    self.dispatch_worker_events(resp)

            except grpc.RpcError as e:
                logging.info(f"gRPC error {e!r}; exiting event loop.")
                print(f"gRPC error {e!r}; exiting event loop.")
                break

        # 4) Clean up
        self.Stop()




    def log_test_result(self, test_res):
        """Log test results to wandb server if enabled"""
        acc = round(test_res["top_1"] / test_res["test_len"], 4)
        acc_5 = round(test_res["top_5"] / test_res["test_len"], 4)
        test_loss = test_res["test_loss"] / test_res["test_len"]
        if self.wandb != None:
            self.wandb.log(
                {
                    "Test/round_to_top1_accuracy": acc,
                    "Test/round_to_top5_accuracy": acc_5,
                    "Test/round_to_loss": test_loss,
                },
                step=self.round,
            )


if __name__ == "__main__":
    executor = Executor(parser.args)
    executor.run()
