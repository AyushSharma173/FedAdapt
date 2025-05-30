# dashboard-backend/app/main.py

import uuid
import subprocess
import copy
import multiprocessing
from typing import Dict, List, Optional
import grpc
from grpc import RpcError
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel




# from fedscale.cloud.config_parser import args as base_args
# import fedscale.cloud.commons as commons
# from fedscale.cloud.aggregation.aggregator import Aggregator
# from fedscale.cloud.execution.executor import Executor
# from fedscale.cloud.channels import job_api_pb2, job_api_pb2_grpc



import grpc


import asyncio, json
from fastapi.responses import StreamingResponse
import logging
import time
from fastapi.responses import JSONResponse


# somewhere at module scope, or per‐request:
# channel = grpc.insecure_channel("127.0.0.1:50051")
# stub   = job_api_pb2_grpc.JobServiceStub(channel)


app = FastAPI(
    title="FedScale Dashboard API",
    version="0.1.0",
    description="Expose client & aggregator state & control for the React dashboard"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Define your allowed origins
# It's always best practice to be explicit instead of using "*"
# allowed_origins = [
#     "http://localhost:3000",  # Keep for local development
#     "https://main.d2wox4wfo4yac.amplifyapp.com" # Your actual AWS Amplify frontend URL
#     # Add any other specific frontend URLs if you have multiple environments (e.g., dev, staging)
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins, # Use the explicit list
#     allow_credentials=True,        # Keep this if your frontend needs to send cookies/auth headers
#     allow_methods=["*"],           # Allows all standard HTTP methods
#     allow_headers=["*"],           # Allows all headers
# )


# Can also use Redis or SQLite later
metrics_history = {} # exp_id -> list of metrics_payload

# ---- Data models ----

# class ExperimentStartRequest(BaseModel):
#     name: str
#     num_executors: int = 1
#     num_clients: int
    

class ExperimentStartRequest(BaseModel):
    name: str

    # Cluster scale & aggregation
    num_executors:        int = 1
    num_clients:          int
    gradient_policy:      str = "FedAvg"
    experiment_mode:      str = "SIMULATION"
    backend:              str = "gloo"
    engine:               str = "PyTorch"

    # Model & data selection
    model_zoo:            str
    model:                str
    data_set:             str
    data_dir:             str
    input_shape:          str  # e.g. "3,224,224"
    output_dim:           int
    num_classes:          int
    embedding_file:       str = ""
    data_map_file:        Optional[str] = None  # Changed to Optional[str] with None as default

    # Training-loop hyperparameters
    rounds:               int = 1
    local_steps:          int = 1
    batch_size:           int = 8
    test_bsz:             int = 8
    learning_rate:        float = 0.01
    min_learning_rate:    float = 0.001
    decay_factor:         float = 0.1
    decay_round:          int = 1
    clip_bound:           float = 1.0
    eval_interval:        int = 1
    dump_epoch:           int = 1

    # Optimization strategy
    optimize_for:        str = "Balanced"   # One of: "Fastest Training", "Balanced", "Best Accuracy"
    compression_limit:   float = 1.0        # Max compression ratio allowed (0.1–1.0)
    auto_tune:           bool = True        # Enable heterogeneity-aware tuning


    # α-mixing hyperparameters
    alpha_threshold: float = 0.02
    alpha_step:      float = 0.10


class ExperimentStatus(BaseModel):
    id: str
    name: str
    num_clients: int
    processes: List[int]  # PIDs
    running: bool


# ---- In-memory registry ----
# maps experiment_id -> dict with keys matching ExperimentStatus
_experiments: Dict[str, Dict] = {}


# ---- worker spawn functions ----

# def _run_aggregator(cfg_overrides: dict):
#     # deep copy the base namespace, then override
#     args = copy.deepcopy(base_args)
#     if args.experiment_mode == "SIMULATION":
#         args.experiment_mode = commons.SIMULATION_MODE
#     for k, v in cfg_overrides.items():
#         setattr(args, k, v)
#     Aggregator(args).run()


# def _run_executor(exp_id: str, rank: int, cfg_overrides: dict):
#     args = copy.deepcopy(base_args)
#     args.experiment_mode = commons.SIMULATION_MODE
#     args.this_rank = rank
#     args.num_executors = 1
#     for k, v in cfg_overrides.items():
#         setattr(args, k, v)
#     args.data_map_file
#     print(f"args.data_map_file: {args.data_map_file}")
#     if args.data_map_file == 'none':
#         args.data_map_file = None
#     print(f"args.data_map_file after modification: {args.data_map_file}")
#     Executor(args).run()


# def get_stub():
#     channel = grpc.insecure_channel(
#         "127.0.0.1:50051",
#         options=[
#             ('grpc.max_receive_message_length', 100 * 1024 * 1024),  # 100MB
#             ('grpc.max_send_message_length', 100 * 1024 * 1024),     # 100MB
#             ('grpc.keepalive_time_ms', 30000),                       # 30 seconds
#             ('grpc.keepalive_timeout_ms', 10000),                    # 10 seconds
#             ('grpc.http2.max_pings_without_data', 0),                # Allow pings without data
#             ('grpc.http2.min_time_between_pings_ms', 10000),         # 10 seconds
#             ('grpc.enable_retries', 1),                              # Enable retries
#             ('grpc.service_config', '{"loadBalancingConfig": [{"round_robin":{}}]}'),  # Round-robin load balancing
#         ]
#     )
    
#     try:
#         # Try to connect with a longer timeout and retry logic
#         for attempt in range(3):  # Try up to 3 times
#             try:
#                 grpc.channel_ready_future(channel).result(timeout=30)  # 30 second timeout
#                 return job_api_pb2_grpc.JobServiceStub(channel)
#             except grpc.FutureTimeoutError:
#                 if attempt == 2:  # Last attempt
#                     logging.error("Failed to connect to aggregator server after 3 attempts")
#                     raise HTTPException(
#                         status_code=503,
#                         detail="Aggregator server is not responding after multiple attempts. Please check if it's running."
#                     )
#                 logging.warning(f"Connection attempt {attempt + 1} failed, retrying...")
#                 time.sleep(2)  # Wait 2 seconds before retrying
#     except Exception as e:
#         logging.error(f"Failed to connect to aggregator server: {str(e)}")
#         raise HTTPException(
#             status_code=503,
#             detail=f"Failed to connect to aggregator server: {str(e)}"
#         )

# ---- Control logic ----
import time
import socket

# @app.post("/experiments", response_model=ExperimentStatus)
# async def create_experiment(req: ExperimentStartRequest):

#     print(f"ExperimentStartRequest: {req}")
#     exp_id = str(uuid.uuid4())

#     # --- all numbers as ints, not strings! ---
#     server_cfg = {
#         "ps_port": 50051,
#         "executor_configs": "127.0.0.1:[{}]".format(req.num_executors),
#         "num_participants": req.num_clients,
#         "num_clients": req.num_clients,
#         "gradient_policy": req.gradient_policy,
#         "experiment_mode": req.experiment_mode,
#         "backend": req.backend,
#         "engine": req.engine,
#         "model_zoo": req.model_zoo,
#         "model": req.model,
#         "data_set": req.data_set,
#         "data_dir": req.data_dir,
#         "input_shape": req.input_shape,
#         "output_dim": req.output_dim,
#         "num_classes": req.num_classes,
#         "embedding_file": req.embedding_file,
#         "rounds": req.rounds,
#         "eval_interval": req.eval_interval,
#         "dump_epoch": req.dump_epoch,
#         "optimize_for": req.optimize_for,
#         "compression_limit": req.compression_limit,
#         "auto_tune": req.auto_tune,
#         "alpha_threshold":  req.alpha_threshold,
#         "alpha_step":       req.alpha_step,
#         "data_map_file":    req.data_map_file,
#         "num_executors":    req.num_executors,


#     }

#     client_cfg = {
#         "ps_ip": "127.0.0.1",
#         "ps_port": 50051,
#         "num_participants": req.num_clients,
#         "num_clients": req.num_clients,
#         "batch_size": req.batch_size,
#         "test_bsz": req.test_bsz,
#         "learning_rate": req.learning_rate,
#         "min_learning_rate": req.min_learning_rate,
#         "decay_factor": req.decay_factor,
#         "decay_round": req.decay_round,
#         "clip_bound": req.clip_bound,
#         "local_steps": req.local_steps,
#         "model_zoo": req.model_zoo,
#         "model": req.model,
#         "data_set": req.data_set,
#         "data_dir": req.data_dir,
#         "input_shape": req.input_shape,
#         "output_dim": req.output_dim,
#         "num_classes": req.num_classes,
#         "embedding_file": req.embedding_file,
#         "backend": req.backend,
#         "engine": req.engine,
#         "optimize_for": req.optimize_for,
#         "compression_limit": req.compression_limit,
#         "auto_tune": req.auto_tune,
#         "alpha_threshold":  req.alpha_threshold,
#         "alpha_step":       req.alpha_step,
#         "data_map_file":    req.data_map_file,
#         "num_executors":    req.num_executors,

#     }

#     print(f"Number of executors: {req.num_executors}")

#     procs = []

#     # 1) start the aggregator
#     p_agg = multiprocessing.Process(
#         target=_run_aggregator, args=(server_cfg, ), daemon=False
#     )
#     p_agg.start()
#     procs.append(p_agg)

#     # 2) wait for gRPC to come up
#     for _ in range(20):
#         try:
#             with socket.create_connection(("127.0.0.1", 50051), timeout=1):
#                 break
#         except OSError:
#             time.sleep(0.5)
#     else:
#         p_agg.terminate()
#         raise RuntimeError("Aggregator gRPC never came up")

#     # 3) launch *one* executor that simulates all clients
#     p_exec = multiprocessing.Process(
#         target=_run_executor, args=(exp_id, 0, client_cfg), daemon=False
#     )
#     p_exec.start()
#     procs.append(p_exec)

#     _experiments[exp_id] = {
#         "id": exp_id,
#         "name": req.name,
#         "num_clients": req.num_clients,
#         "processes": [p.pid for p in procs],
#         "running": True,
#     }
#     return ExperimentStatus(**_experiments[exp_id])



@app.get("/experiments", response_model=List[ExperimentStatus])
async def list_experiments():
    # return [ExperimentStatus(**exp) for exp in _experiments.values()]
    return list(_experiments.values())


@app.post("/experiments/{exp_id}/stop", response_model=ExperimentStatus)
async def stop_experiment(exp_id: str):
    exp = _experiments.get(exp_id)
    if not exp:
        raise HTTPException(404, "Experiment not found")
    if not exp["running"]:
        raise HTTPException(400, "Experiment already stopped")

    # kill each PID
    for pid in exp["processes"]:
        subprocess.run(["kill", "-TERM", str(pid)], check=False)

    exp["running"] = False
    return ExperimentStatus(**exp)



# @app.get("/experiments/{exp_id}/status")
# async def experiment_status(exp_id: str):
#     stub = get_stub()
#     resp = stub.GetAggregatorStatus(job_api_pb2.StatusRequest())
#     return {
#       "round": resp.current_round,
#       "running": resp.is_running,
#       "virtual_clock": resp.global_virtual_clock,
#       "sampled_clients": list(resp.sampled_clients),
#     }

# @app.get("/experiments/{exp_id}/round/{r}/metrics")
# async def round_metrics(exp_id: str, r: int):
#     stub = get_stub()
#     try:
#         resp = stub.GetRoundMetrics(job_api_pb2.MetricsRequest(round=r))
#     except grpc.RpcError as e:
#         if e.code() == grpc.StatusCode.NOT_FOUND:
#             raise HTTPException(404, f"No metrics for round {r}")
#         else:
#             raise HTTPException(500, e.details())

#     return {
#       "round":     resp.round,
#       "test_loss": resp.test_loss,
#       "top1":      resp.test_accuracy1,
#       "top5":      resp.test_accuracy5,
#       "clients": [
#         {
#           "id":       cm.client_id,
#           "loss":     cm.loss,
#           "utility":  cm.utility,
#           "duration": cm.duration,
#           "loss_curve": list(cm.loss_curve),
#           "client_eval_local_acc": cm.client_eval_local_acc,
#           "client_eval_global_acc": cm.client_eval_local_loss,
#           "client_alpha": cm.client_alpha,   
#         }
#         for cm in resp.clients
#       ],
#     }



# @app.get("/experiments/{exp_id}/stream")
# async def experiment_stream(exp_id: str):
#     last_round_emitted = 0
#     stub = get_stub()

#     async def event_generator():
#         nonlocal last_round_emitted

#         # === NEW: Send history first ===
#         if exp_id in metrics_history:
#             for cached in metrics_history[exp_id]:
#                 yield f"data: {json.dumps(cached)}\n\n"
#                 last_round_emitted = cached["round"]  # so we don't reprocess these later

#         while True:
#             try:
#                 status = stub.GetAggregatorStatus(job_api_pb2.StatusRequest())
#             except RpcError:
#                 break

#             status_payload = {
#                 "type":            "status",
#                 "round":           status.current_round,
#                 "running":         status.is_running,
#                 "virtual_clock":   status.global_virtual_clock,
#                 "sampled_clients": list(status.sampled_clients),
#             }
#             yield f"data: {json.dumps(status_payload)}\n\n"

#             r = status.current_round
#             if r >= 1 and (r-1) > last_round_emitted:
#                 try:
#                     m = stub.GetRoundMetrics(job_api_pb2.MetricsRequest(round=r-1))
#                 except RpcError:
#                     pass
#                 else:
#                     if len(m.clients) > 0:
#                         last_round_emitted = m.round

#                         clients = [
#                             {
#                                 "id":         cm.client_id,
#                                 "loss":       cm.loss,
#                                 "utility":    cm.utility,
#                                 "duration":   cm.duration,
#                                 "loss_curve": list(cm.loss_curve),
#                                 "client_eval_local_acc": cm.client_eval_local_acc,
#                                 "client_eval_global_acc": cm.client_eval_global_acc,
#                                 "client_alpha": cm.client_alpha, 
#                             }
#                             for cm in m.clients
#                         ]
#                         metrics_payload = {
#                             "type":      "metrics",
#                             "round":     m.round,
#                             "test_loss": m.test_loss,
#                             "top1":      m.test_accuracy1,
#                             "top5":      m.test_accuracy5,
#                             "clients":   clients,
#                         }

#                         # Cache it
#                         if exp_id not in metrics_history:
#                             metrics_history[exp_id] = []

#                         rounds_seen = {m["round"] for m in metrics_history[exp_id]}

#                         if m.round not in rounds_seen:
#                             metrics_history[exp_id].append(metrics_payload)

#                         yield f"data: {json.dumps(metrics_payload)}\n\n"

#             if not status.is_running:
#                 break
#             await asyncio.sleep(1.0)

#     return StreamingResponse(event_generator(), media_type="text/event-stream")


import os



def summarize_structure(obj, *, indent=0, max_depth=3, max_list_len=3):
    """
    Recursively print keys/types of obj (dicts/lists), but:
      - Only descend max_depth levels
      - Only show up to max_list_len items of any list, then elide the rest
    """
    prefix = "  " * indent
    if indent > max_depth:
        print(prefix + "…")
        return

    if isinstance(obj, dict):
        print(prefix + "{")
        for k, v in obj.items():
            print(f"{prefix}  {k!r}: ", end="")
            summarize_structure(v, indent=indent+1,
                                max_depth=max_depth,
                                max_list_len=max_list_len)
        print(prefix + "}")
    elif isinstance(obj, list):
        print(prefix + f"[List len={len(obj)}]")
        for i, item in enumerate(obj[:max_list_len]):
            print(f"{prefix}  [{i}]: ", end="")
            summarize_structure(item, indent=indent+1,
                                max_depth=max_depth,
                                max_list_len=max_list_len)
        if len(obj) > max_list_len:
            print(prefix + f"  … ({len(obj)-max_list_len} more items)")
    else:
        # Leaf value: just print its type (and maybe a sample repr)
        val = obj
        typ = type(val).__name__
        if isinstance(val, (str, int, float, bool)):
            print(prefix + repr(val))
        else:
            print(prefix + f"<{typ}>")

def summarize_payloads(payloads, **kwargs):
    for i, p in enumerate(payloads):
        print(f"\n=== payloads[{i}] summary ===")
        summarize_structure(p, **kwargs)



@app.get("/experiments/{exp_id}/data")
async def experiment_data(exp_id: str):
    """
    Serve up the pre–generated JSON payloads for a given experiment
    (i.e. all of the per-algorithm files in data/{exp_id}/).
    """
    folder = os.path.join("data", exp_id)
    if not os.path.isdir(folder):
        raise HTTPException(404, f"No data folder for experiment {exp_id}")

    payloads = []
    # load every .json in that folder
    for fn in sorted(os.listdir(folder)):
        if fn.endswith(".json"):
            path = os.path.join(folder, fn)
            with open(path, "r") as f:
                payloads.append(json.load(f))

    summarize_payloads(payloads, max_depth=2, max_list_len=2)
    return payloads



# @app.get("/experiments/{exp_id}/static")
# def get_static(exp_id: str):
#     # look under data/{exp_id}/fedavg.json
#     path = os.path.join("data", exp_id, "fedavg.json")
#     if not os.path.exists(path):
#         # log to console for debugging
#         print(f"No static data for experiment {exp_id} in {path}")
#         raise HTTPException(
#             status_code=404,
#             detail=f"No static data for experiment '{exp_id}'"
#         )

#     # load the file as JSON and return it directly
#     with open(path, "r") as f:
#         payload = json.load(f)
#     return payload


@app.get("/experiments/{static_id}/static")
def get_static(static_id: str):
    """
    static_id should be of the form "<expName>-<variant>",
    e.g. "experiment1-fedavg".
    We split on the first dash, look under data/<expName>/<variant>.json
    """
    # split into experiment folder and json basename
    if "-" not in static_id:
        raise HTTPException(
            status_code=400,
            detail="static_id must be '<experimentName>-<variant>'"
        )
    exp_name, variant = static_id.split("-", 1)
    # normalize variant filename (e.g. drop any extra hyphens)
    variant = variant.replace("-", "").lower()

    path = os.path.join("data", exp_name, f"{variant}.json")
    if not os.path.exists(path):
        print(f"No static data for '{static_id}' (tried {path})")
        raise HTTPException(
            status_code=404,
            detail=f"No static data for '{static_id}' (tried {path})"
        )

    with open(path, "r") as f:
        payload = json.load(f)
    return payload


@app.get("/health")
async def health():
    return {"status": "ok"}


# To run:
# uvicorn app.main:app --reload --port 8000
