#!/usr/bin/env python3
import os
import json
import numpy as np

def logistic_curve(rounds, k, x0, y0, y_max):
    """Generate a logistic growth curve."""
    return y0 + (y_max - y0) / (1 + np.exp(-k * (rounds - x0)))

def generate_selfadaptive_json():
    # Experiment settings
    num_clients      = 100
    rounds_total     = 200
    eval_interval    = 10
    local_steps      = 1
    batch_size       = 32
    learning_rate    = 0.05
    seed             = 42
    noise_std        = 0.01
    partition_alpha  = 0.5

    # α-mixing hyperparameters for this variant
    alpha_threshold = 0.02
    alpha_step      = 0.10

    # 1) Global accuracy curve parameters for Self-Adaptive
    rounds = np.arange(0, rounds_total + 1)
    # growth rate k, midpoint x0, baseline y0, max accuracy y_max
    k, x0, y0, y_max = (0.05, 85, 0.10, 0.72)
    base = logistic_curve(rounds, k, x0, y0, y_max)

    np.random.seed(seed)
    curve = base + np.random.normal(scale=noise_std, size=rounds.shape)
    # inject occasional dips/spikes
    for _ in range(10):
        idx = np.random.randint(75, 151)
        curve[idx:idx+3] += np.random.choice([-1, 1]) * np.random.uniform(0.01, 0.03)
    curve = np.clip(curve, y0, y_max)

    # 2) Build the timeline
    timeline = []

    # --- initial status at round 0 ---
    timeline.append({
        "type":            "status",
        "round":           0,
        "running":         True,
        "virtual_clock":   0.0,
        "sampled_clients": list(range(num_clients))
    })

    # --- metrics at each eval interval ---
    for r in range(eval_interval, rounds_total + 1, eval_interval):
        top1 = float(curve[r])
        top5 = top1  # same metric for simplicity

        # per-client metrics for this round
        clients = []
        for cid in range(num_clients):
            # simulate a small variation in local vs global accuracy
            local_acc = float(np.clip(top1 + np.random.normal(scale=0.01), 0.0, 1.0))

            # simulate a local loss‐curve of length 10 for each client
            loss_curve = []
            base_loss = 1.0
            for step in range(10):
                v = base_loss - (step * 0.05) + np.random.normal(scale=0.01)
                loss_curve.append(float(np.clip(v, 0.0, 1.0)))

            # simulate the α value each client used this round (just constant here)
            clients.append({
                "id":                        cid,
                "loss_curve":               loss_curve,
                "client_eval_local_acc":    local_acc,
                "client_eval_global_acc":   top1,
                "client_alpha":             alpha_threshold  # for demonstration
            })

        timeline.append({
            "type":    "metrics",
            "round":   r,
            "top1":    top1,
            "top5":    top5,
            "clients": clients
        })

    # --- final status (experiment finished) ---
    timeline.append({
        "type":            "status",
        "round":           rounds_total,
        "running":         False,
        "virtual_clock":   float(rounds_total),
        "sampled_clients": list(range(num_clients))
    })

    # 3) Assemble full JSON
    out = {
        "id":           "selfadaptive",
        "name":         "Self-Adaptive on CIFAR-10 (Dirichlet α=0.5)",
        "description":  "Clients mix local/global with self-adaptive α per round.",
        "dataset": {
            "name":       "CIFAR-10",
            "train_size": 50000,
            "test_size":  10000
        },
        "partition": {
            "method":      "dirichlet",
            "alpha":       partition_alpha,
            "num_clients": num_clients
        },
        "hyperparameters": {
            "rounds":                rounds_total,
            "local_steps":           local_steps,
            "batch_size":            batch_size,
            "learning_rate":         learning_rate,
            "eval_interval":         eval_interval,
            "seed":                  seed,
            "measurement_noise_std": noise_std
        },
        "algorithm": {
            "name":   "Self-Adaptive",
            "params": {
                "alpha_threshold": alpha_threshold,
                "alpha_step":      alpha_step
            }
        },
        "timeline": timeline
    }

    # 4) Write to file
    folder = os.path.join("data", "experiment2")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "selfadaptive.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote static experiment data to {path}")

if __name__ == "__main__":
    generate_selfadaptive_json()
