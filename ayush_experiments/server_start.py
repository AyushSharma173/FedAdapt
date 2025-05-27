# import multiprocessing
# from multiprocessing import freeze_support
# import sys
# from argparse import Namespace

# import fedscale.cloud.commons as commons
# from fedscale.cloud.aggregation.aggregator import Aggregator

# # Clear stray argv
# sys.argv = ['']

# # Define every field Aggregator expects:
# parser_args = Namespace(
#     experiment_mode=commons.SIMULATION_MODE,
#     use_cuda=False,
#     cuda_device=None,
#     device_conf_file="",

#     # gRPC/server config
#     ps_port=50051,
#     executor_configs="127.0.0.1:[1]",
#     connection_timeout=60,

#     # FL hyperparameters
#     job_name="demo_job",
#     time_stamp="ts1",
#     data_set="cifar10",
#     model="resnet20_cifar10",
#     sample_mode="random",
#     gradient_policy="fedavg",
#     task="cv",
#     cfg_file=None,
#     data_dir="./data",

#     # client-side training config
#     local_steps=1,
#     batch_size=32,

#     # federation rounds
#     # num_participants=1,
#     num_participants=4,
#     rounds=10,
#     eval_interval=1,
#     overcommitment=1.3,
#     learning_rate=0.01,
#     decay_round=5,
#     decay_factor=0.5,
#     min_learning_rate=1e-5,

#     # logging & checkpointing
#     wandb_token="",
#     save_checkpoint=False,
#     log_path="./logs",
#     filter_less=0,
#     filter_more=100000,

#     device_avail_file=None,
#     client_timeout=10,
#     client_retry_interval=1,
#     client_retry_max=3,

#     this_rank=0,
#     num_executors=1,
#     ps_ip="127.0.0.1",
#     engine=commons.PYTORCH,
#     model_zoo="fedscale-torch-zoo",
#     num_class=10,
#     data_map_file=None,
#     memory_capacity=0,
#     test_bsz=32,
# )


# from fedscale.cloud import config_parser
# def main():
#     parser_args = config_parser
#     aggregator = Aggregator(parser_args)
#     aggregator.run()


# if __name__ == "__main__":
#     freeze_support()
#     multiprocessing.set_start_method("fork")
#     main()










import sys
import multiprocessing
from multiprocessing import freeze_support

# 1) again, clear argv noise
sys.argv = ['']

from fedscale.cloud.config_parser import args
import fedscale.cloud.commons as commons
from fedscale.cloud.aggregation.aggregator import Aggregator

def main():
    # 2) override your server’s view of the world:
    args.ps_port          = "50051"
    args.executor_configs = "127.0.0.1:[1]"  # one host, four logical clients
    args.num_executors    = 1               # how many Executor processes you’ll launch
    args.num_participants = 4               # clients sampled per round
    args.rounds           = 10
    args.eval_interval    = 1
    args.learning_rate    = 0.01
    args.model_zoo      = "fedscale-torch-zoo"
    args.model            = "resnet20_cifar10"
    # …plus any other FL hyperparams you want to set in code.

    aggregator = Aggregator(args)
    aggregator.run()

if __name__ == "__main__":
    freeze_support()
    multiprocessing.set_start_method("fork")
    main()
