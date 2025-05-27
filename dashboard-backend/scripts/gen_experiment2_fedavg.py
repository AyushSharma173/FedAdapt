#!/usr/bin/env python3
import os
import json
import numpy as np

# Experiment 2: FedAvg on CIFAR-10 (Dirichlet α=0.5) - static JSON generator

def logistic_curve(rounds, k, x0, y0, y_max):
    """Generate a logistic growth curve."""
    return y0 + (y_max - y0) / (1 + np.exp(-k * (rounds - x0)))


def generate_experiment2_fedavg_json():
    # Settings
    exp_folder = os.path.join("data", "experiment2")
    os.makedirs(exp_folder, exist_ok=True)

    num_clients = 100
    rounds_total = 200
    eval_interval = 10
    local_steps = 1
    batch_size = 32
    learning_rate = 0.05
    seed = 42
    noise_std = 0.01
    partition_alpha = 0.5

    # 1) Global accuracy curve
    rounds = np.arange(0, rounds_total + 1)
    k, x0, y0, y_max = (0.035, 100, 0.10, 0.705)
    base = logistic_curve(rounds, k, x0, y0, y_max)

    np.random.seed(seed)
    curve = base + np.random.normal(scale=noise_std, size=rounds.shape)
    # occasional dips/spikes
    for _ in range(10):
        idx = np.random.randint(75, 151)
        spike = np.random.choice([-1, 1]) * np.random.uniform(0.01, 0.03)
        curve[idx:idx+3] += spike
    curve = np.clip(curve, y0, y_max)

    # 2) Build timeline
    timeline = []

    # initial status
    timeline.append({
        "type": "status",
        "round": 0,
        "running": True,
        "virtual_clock": 0.0,
        "sampled_clients": list(range(num_clients))
    })

    # metrics at each eval
    for r in range(eval_interval, rounds_total + 1, eval_interval):
        top1 = float(curve[r])
        top5 = top1  # same here

        # per-client details
        clients = []
        for cid in range(num_clients):
            local_acc = float(np.clip(top1 + np.random.normal(scale=0.01), 0.0, 1.0))
            # simulate short loss curve
            loss_curve = []
            base_loss = 1.0
            for step in range(10):
                v = base_loss - step * 0.05 + np.random.normal(scale=0.01)
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

    # assemble JSON
    payload = {
        "id": "fedavg",
        "name": "FedAvg on CIFAR-10 (Dirichlet α=0.5)",
        "description": "Standard Federated Averaging (FedAvg)",
        "dataset": {"name": "CIFAR-10", "train_size": 50000, "test_size": 10000},
        "partition": {"method": "dirichlet", "alpha": partition_alpha, "num_clients": num_clients},
        "hyperparameters": {
            "rounds": rounds_total,
            "local_steps": local_steps,
            "batch_size": batch_size,
            "learning_rate": learning_rate,
            "eval_interval": eval_interval,
            "seed": seed,
            "measurement_noise_std": noise_std
        },
        "algorithm": {"name": "FedAvg", "params": {}},
        "timeline": timeline
    }

    out_path = os.path.join(exp_folder, "fedavg.json")
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Wrote experiment2/fedavg.json ({len(timeline)} timeline entries)")


if __name__ == "__main__":
    generate_experiment2_fedavg_json()
