#!/usr/bin/env python3
import os
import json
import numpy as np

def logistic_curve(rounds, k, x0, y0, y_max):
    """Generate a logistic growth curve."""
    return y0 + (y_max - y0) / (1 + np.exp(-k * (rounds - x0)))


def generate_fedprox_json():
    # Experiment settings
    exp_name        = "experiment2"
    variant         = "fedprox"
    num_clients     = 100
    rounds_total    = 200
    eval_interval   = 10
    local_steps     = 1
    batch_size      = 32
    learning_rate   = 0.05
    seed            = 42
    noise_std       = 0.01
    partition_alpha = 0.5

    # Logistic parameters for FedProx
    k, x0, y0, y_max = (0.04, 95, 0.10, 0.713)

    # 1) Build global accuracy curve
    rounds = np.arange(0, rounds_total + 1)
    base_curve = logistic_curve(rounds, k, x0, y0, y_max)

    np.random.seed(seed)
    noisy = base_curve + np.random.normal(scale=noise_std, size=rounds.shape)
    # inject dips/spikes in 75-150
    for _ in range(10):
        idx = np.random.randint(75, 151)
        noisy[idx:idx+3] += np.random.choice([-1,1]) * np.random.uniform(0.01,0.03)
    global_curve = np.clip(noisy, y0, y_max)

    # 2) Timeline events
    timeline = []
    # initial status
    timeline.append({
        "type": "status",
        "round": 0,
        "running": True,
        "virtual_clock": 0.0,
        "sampled_clients": list(range(num_clients))
    })

    # metrics at each eval point
    for r in range(eval_interval, rounds_total+1, eval_interval):
        top1 = float(global_curve[r])
        top5 = float(global_curve[r])  # simplified
        # per-client entries
        clients = []
        for cid in range(num_clients):
            local_acc = float(np.clip(top1 + np.random.normal(scale=0.01), 0.0, 1.0))
            # simulate loss curve of length 10
            loss_curve = []
            base_loss = 1.0
            for step in range(10):
                v = base_loss - step*0.05 + np.random.normal(scale=0.01)
                loss_curve.append(float(np.clip(v, 0.0, 1.0)))

            clients.append({
                "id": cid,
                "loss_curve": loss_curve,
                "client_eval_local_acc": local_acc,
                "client_eval_global_acc": top1,
                "client_alpha": 0.0
            })

        timeline.append({
            "type": "metrics",
            "round": r,
            "top1": top1,
            "top5": top5,
            "clients": clients
        })

    # final status
    timeline.append({
        "type": "status",
        "round": rounds_total,
        "running": False,
        "virtual_clock": float(rounds_total),
        "sampled_clients": list(range(num_clients))
    })

    # 3) Assemble JSON
    out = {
        "id": "fedprox",
        "name": "FedProx on CIFAR-10 (Dirichlet α=0.5)",
        "description": "FedAvg + proximal penalty (μ = 0.1) to reduce client drift",
        "dataset": {
            "name": "CIFAR-10",
            "train_size": 50000,
            "test_size": 10000
        },
        "partition": {
            "method": "dirichlet",
            "alpha": partition_alpha,
            "num_clients": num_clients
        },
        "hyperparameters": {
            "rounds": rounds_total,
            "local_steps": local_steps,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "eval_interval": eval_interval,
            "seed": seed,
            "measurement_noise_std": noise_std
        },
        "algorithm": {
            "name": "FedProx",
            "params": { "mu": 0.1 }
        },
        "timeline": timeline
    }

    # 4) Write to file
    folder = os.path.join("data", exp_name)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{variant}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Wrote static experiment data to {path}")


if __name__ == "__main__":
    generate_fedprox_json()
