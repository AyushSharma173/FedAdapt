# import multiprocessing
# from multiprocessing import freeze_support
# import sys
# from argparse import Namespace

# import fedscale.cloud.commons as commons
# from fedscale.cloud.execution.executor import Executor


# def main():
#     # Parse rank and total executors from command line, or default to 0,1
#     if len(sys.argv) >= 3:
#         this_rank = int(sys.argv[1])
#         num_executors = int(sys.argv[2])
#     else:
#         this_rank = 0
#         num_executors = 1

#     # Build the args Namespace for Executor
#     args = Namespace(
#         use_cuda=False,
#         cuda_device=0,
#         # num_executors=num_executors,
#         # this_rank=this_rank,
#         num_executors=1,
#         this_rank=0,
#         ps_ip="127.0.0.1",
#         ps_port=50051,
#         wandb_token="",
#         job_name="demo_job",
#         time_stamp="123456",
#         task="cv",
#         engine=commons.PYTORCH,
#         model="resnet20_cifar10",
#         model_zoo="fedscale-torch-zoo",
#         data_set="cifar10",
#         data_dir="./data",
#         num_class=10,
#         # num_participants=num_executors,
#         num_participants=4,
#         data_map_file=None,
#         memory_capacity=0,
#         test_bsz=32,
#         log_path="./logs",
#         test_ratio=0.1,
#         test_interval=1,
#         test_epochs=1,
#         test_batch_size=32,
#         test_num_workers=4,
#         test_pin_memory=True,
#         batch_size=128,
#         local_steps=1,
#         learning_rate=0.01,
#         momentum=0.9,
#         weight_decay=0.0001,
#         device_conf_file=None,
#         experiment_mode=commons.SIMULATION_MODE,
#         num_loaders=4,
#         pin_memory=False,
#         num_workers=1,
#         # num_clients=num_executors,
#         num_clients=4,
#         num_rounds=1,
#         num_epochs=1,
#         gradient_policy="fedavg",
#         overcommitment=1.3,
#         decay_round=5,
#         decay_factor=0.5,
#         min_learning_rate=1e-5,
#         save_checkpoint=True,
#         filter_less=0,
#     )

#     executor = Executor(args)
#     executor.run()


# if __name__ == "__main__":
#     freeze_support()
#     multiprocessing.set_start_method("fork")
#     main()





#!/usr/bin/env python3
import sys
import multiprocessing
from multiprocessing import freeze_support

# 1) First grab just the flags you want to override
import argparse
flag_parser = argparse.ArgumentParser(add_help=False)
flag_parser.add_argument(
    "--this_rank", type=int, default=None,
    help="Which executor rank is this process (0-based)"
)
flag_parser.add_argument(
    "--num_executors", type=int, default=None,
    help="(Optional) how many executor procs you'll be running"
)
flags, _ = flag_parser.parse_known_args()

# 2) Now import FedScale’s own parser (it will consume the rest of sys.argv for defaults)
from fedscale.cloud.config_parser import args
import fedscale.cloud.commons as commons
from fedscale.cloud.execution.executor import Executor

# 3) Override whatever you like in code, but honor any flags:
args.ps_ip            = "127.0.0.1"
args.ps_port          = "50051"
args.experiment_mode  = commons.SIMULATION_MODE
if flags.this_rank is not None:
    args.this_rank    = flags.this_rank
if flags.num_executors is not None:
    args.num_executors = flags.num_executors

# simulate 4 logical clients inside this one process:
args.num_participants = 4      # how many get picked per round
args.batch_size       = 128
args.local_steps      = 1
args.rounds           = 1
args.model_zoo        = "fedscale-torch-zoo"
args.model            = "resnet20_cifar10"
# …any other tweaks you want…

def main():
    executor = Executor(args)
    executor.run()

if __name__ == "__main__":
    # macOS needs "fork" for multiprocessing
    freeze_support()
    multiprocessing.set_start_method("fork")
    main()
