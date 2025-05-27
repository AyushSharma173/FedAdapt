# #!/usr/bin/env python3
# import os, json, numpy as np

# def two_phase_curve(r, k1, x01, k2, x02, y0, ymid, y_max):
#     p1 = y0 + (ymid - y0) / (1 + np.exp(-k1*(r-x01)))
#     p2 = ymid + (y_max-ymid) / (1 + np.exp(-k2*(r-x02)))
#     alpha = np.clip((r - x01)/(x02-x01), 0, 1)
#     return (1-alpha)*p1 + alpha*p2

# def generate_fedavg_json():
#     num_clients, rounds_total, eval_interval = 100, 200, 10
#     seed = 42; np.random.seed(seed)
#     # global two-phase base curve
#     rounds = np.arange(0, rounds_total+1)
#     global_base = two_phase_curve(rounds,
#                                  k1=0.1, x01=20, 
#                                  k2=0.03, x02=120,
#                                  y0=0.10, ymid=0.50, y_max=0.705)
#     # correlated dips
#     for dr in np.random.choice(np.arange(75,150), 3, replace=False):
#         global_base[dr:dr+5] -= np.random.uniform(0.02, 0.05)
#     noise_std = 0.01
#     global_curve = np.clip(global_base + np.random.normal(scale=noise_std, size=rounds.shape),
#                            0.10, 0.705)

#     timeline = [{
#       "type":"status","round":0,"running":True,"virtual_clock":0.0,
#       "sampled_clients": list(range(num_clients))
#     }]

#     # per-round metrics
#     vc = 0.0
#     for r in range(eval_interval, rounds_total+1, eval_interval):
#         top1 = float(global_curve[r])
#         top5 = top1 + np.random.uniform(0.001, 0.005)  # top5 slightly better
#         clients = []
#         # simulate heterogeneity in curves & times
#         comp_times = np.random.lognormal(mean=0, sigma=0.5, size=num_clients)
#         comm_times = np.random.lognormal(mean=-2, sigma=0.3, size=num_clients)
#         for cid in range(num_clients):
#             # client-specific curve: slight k/x0 variation
#             k_c  = np.random.uniform(0.9,1.1)*0.035
#             x0_c = 100 + np.random.randint(-15,15)
#             y_max_c = 0.705 + np.random.uniform(-0.01,0.01)
#             base_c = 0.10 + (y_max_c-0.10)/(1+np.exp(-k_c*(r-x0_c)))
#             local_curve_val = float(np.clip(base_c + np.random.normal(scale=noise_std*1.5), 0.0,1.0))
#             # realistic local loss decay
#             loss_curve=[]
#             for step in range(10):
#                 decay = 1.0 * np.exp(-0.3*step)
#                 loss_curve.append(float(np.clip(decay + np.random.normal(scale=0.02),0,1)))
#             clients.append({
#               "id": cid,
#               "loss_curve":      loss_curve,
#               "client_eval_local_acc":   np.clip(local_curve_val,0,1),
#               "client_eval_global_acc":  top1,
#               "client_alpha":    0.0,
#               "client_comp_time": comp_times[cid],
#               "client_comm_time": comm_times[cid]
#             })
#         # bump virtual clock by the slowest client this round
#         vc += float(max(comp_times)*1 + np.mean(comm_times)*0.1)
#         timeline.append({
#           "type":"metrics","round":r,"top1":top1,"top5":top5,
#           "virtual_clock":vc,
#           "clients":clients
#         })

#     timeline.append({
#       "type":"status","round":rounds_total,"running":False,
#       "virtual_clock":vc,
#       "sampled_clients": list(range(num_clients))
#     })

#     out = {
#       "id":"fedavg","name":"FedAvg on CIFAR-10 (Dirichlet α=0.5)",
#       # … dataset, partition, hyperparameters …
#       "timeline": timeline
#     }
#     os.makedirs("data/experiment1", exist_ok=True)
#     with open("data/experiment1/fedavg.json","w") as f:
#         json.dump(out, f, indent=2)
#     print("Wrote realistic fedavg.json")





# if __name__ == "__main__":
#     generate_fedavg_json()


#!/usr/bin/env python3
import os
import json
import numpy as np

def two_phase_curve(r, k1, x01, k2, x02, y0, ymid, y_max):
    p1 = y0 + (ymid - y0) / (1 + np.exp(-k1*(r-x01)))
    p2 = ymid + (y_max-ymid) / (1 + np.exp(-k2*(r-x02)))
    alpha = np.clip((r - x01)/(x02-x01), 0, 1)
    return (1-alpha)*p1 + alpha*p2

def generate_fedavg_json():
    # --- Configuration ---
    num_clients    = 100
    rounds_total   = 200
    eval_interval  = 10
    seed           = 42
    noise_std      = 0.01

    np.random.seed(seed)

    # --- Global Two-Phase Accuracy Curve ---
    rounds      = np.arange(0, rounds_total+1)
    global_base = two_phase_curve(
        rounds,
        k1=0.1, x01=20,
        k2=0.03, x02=120,
        y0=0.10, ymid=0.50, y_max=0.705
    )
    # introduce a few dips
    for dr in np.random.choice(np.arange(75,150), 3, replace=False):
        global_base[dr:dr+5] -= np.random.uniform(0.02, 0.05)
    global_curve = np.clip(
        global_base + np.random.normal(scale=noise_std, size=rounds.shape),
        0.10, 0.705
    )

    # --- Build Timeline ---
    timeline = [{
        "type": "status",
        "round": 0,
        "running": True,
        "virtual_clock": 0.0,
        "sampled_clients": list(range(num_clients))
    }]

    vc = 0.0
    for r in range(eval_interval, rounds_total+1, eval_interval):
        top1 = float(global_curve[r])
        top5 = top1 + np.random.uniform(0.001, 0.005)

        # simulate client heterogeneity
        comp_times = np.random.lognormal(mean=0, sigma=0.5, size=num_clients)
        comm_times = np.random.lognormal(mean=-2, sigma=0.3, size=num_clients)

        clients = []
        for cid in range(num_clients):
            # per-client accuracy simulation
            k_c      = np.random.uniform(0.9, 1.1) * 0.035
            x0_c     = 100 + np.random.randint(-15, 15)
            y_max_c  = 0.705 + np.random.uniform(-0.01, 0.01)
            base_c   = 0.10 + (y_max_c - 0.10) / (1 + np.exp(-k_c*(r-x0_c)))
            local_acc = float(np.clip(base_c + np.random.normal(scale=noise_std*1.5), 0, 1))

            # synthetic loss curve for local training
            loss_curve = []
            for step in range(10):
                decay = np.exp(-0.3 * step)
                loss_curve.append(float(np.clip(decay + np.random.normal(scale=0.02), 0, 1)))

            clients.append({
                "id": cid,
                "loss_curve":             loss_curve,
                "client_eval_local_acc":  local_acc,
                "client_eval_global_acc": top1,
                "client_alpha":           0.0,
                "client_comp_time":       float(comp_times[cid]),
                "client_comm_time":       float(comm_times[cid])
            })

        # advance virtual clock by the slowest comp + avg comm
        vc += float(max(comp_times) + np.mean(comm_times)*0.1)

        timeline.append({
            "type":           "metrics",
            "round":          r,
            "top1":           top1,
            "top5":           top5,
            "virtual_clock":  vc,
            "clients":        clients
        })

    timeline.append({
        "type": "status",
        "round": rounds_total,
        "running": False,
        "virtual_clock": vc,
        "sampled_clients": list(range(num_clients))
    })

    # --- Package Full JSON with Metadata ---
    out = {
        "id":   "fedavg",
        "name": "FedAvg on CIFAR-10 (Dirichlet α=0.5)",

        "dataset": {
            "name":       "CIFAR-10",
            "train_size": 50000,
            "test_size":  10000
        },
        "partition": {
            "method":      "Dirichlet",
            "alpha":       0.5,
            "num_clients": num_clients
        },
        "hyperparameters": {
            "rounds":                  rounds_total,
            "local_steps":             5,
            "batch_size":              32,
            "learning_rate":           0.01,
            "eval_interval":           eval_interval,
            "seed":                    seed,
            "measurement_noise_std":   noise_std
        },
        "algorithm": {
            "name":   "FedAvg",
            "params": {}
        },

        "timeline": timeline
    }

    # --- Write to Disk ---
    os.makedirs("data/experiment1", exist_ok=True)
    with open("data/experiment1/fedavg.json", "w") as f:
        json.dump(out, f, indent=2)

    print("Wrote realistic fedavg.json")

if __name__ == "__main__":
    generate_fedavg_json()
