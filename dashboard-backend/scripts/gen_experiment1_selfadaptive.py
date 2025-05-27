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

    # Self-adaptive hyperparameters
    tau   = 0.005   # threshold
    delta = 0.10   # α step size


    client_bias = np.random.RandomState(seed).normal(loc=0, scale=0.02, size=num_clients)
    
    # 1) Global accuracy curve
    rounds = np.arange(0, rounds_total + 1)
    k, x0, y0, y_max = (0.05, 85, 0.10, 0.72)
    base = logistic_curve(rounds, k, x0, y0, y_max)

    np.random.seed(seed)
    global_curve = base + np.random.normal(scale=noise_std, size=rounds.shape)
    # occasional dips/spikes
    for _ in range(10):
        idx = np.random.randint(75, 151)
        perturb = np.random.choice([-1, 1]) * np.random.uniform(0.01, 0.03)
        global_curve[idx:idx+3] += perturb
    global_curve = np.clip(global_curve, y0, y_max)

    # 2) Initialize per-client α
    alphas = np.full(num_clients, 0.5, dtype=float)

    # 3) Build the timeline
    timeline = []
    # initial status
    timeline.append({
        "type":          "status",
        "round":         0,
        "running":       True,
        "virtual_clock": 0.0,
        "sampled_clients": list(range(num_clients))
    })

    # metrics every eval_interval rounds
    for r in range(eval_interval, rounds_total + 1, eval_interval):
        top1 = float(global_curve[r])
        top5 = top1  # can tweak top5 > top1 if desired

        clients = []
        for cid in range(num_clients):
            # simulate local accuracy with a bit of noise
            # local_acc = float(np.clip(top1 + np.random.normal(scale=0.01), 0.0, 1.0))

            # 1) build the noisy, biased local accuracy
            raw_acc = (
                top1
                + client_bias[cid]          # persistent bias
                + np.random.normal(scale=0.015)    # noise
            )
            # 2) clip into [0,1]
            local_acc = float(np.clip(raw_acc, 0.0, 1.0))


            # update α for this client
            diff = local_acc - top1
            if diff > tau:
                alphas[cid] = min(alphas[cid] + delta, 1.0)
            elif diff < -tau:
                alphas[cid] = max(alphas[cid] - delta, 0.0)
            # else α stays

            # simulate a small per-client loss curve of length 10
            loss_curve = []
            base_loss = 1.0
            for step in range(10):
                v = base_loss - (step * 0.05) + np.random.normal(scale=0.01)
                loss_curve.append(float(np.clip(v, 0.0, 1.0)))

            clients.append({
                "id":                     cid,
                "loss_curve":            loss_curve,
                "client_eval_local_acc":  local_acc,
                "client_eval_global_acc": top1,
                "client_alpha":          float(alphas[cid])
            })

        timeline.append({
            "type":    "metrics",
            "round":   r,
            "top1":    top1,
            "top5":    top5,
            "clients": clients
        })

    # final status
    timeline.append({
        "type":          "status",
        "round":         rounds_total,
        "running":       False,
        "virtual_clock": float(rounds_total),
        "sampled_clients": list(range(num_clients))
    })

    # 4) Assemble JSON
    out = {
        "id":           "self-adaptive",
        "name":         "Self-Adaptive on CIFAR-10 (Dirichlet α=0.5)",
        "description":  "Clients mix local vs global via self-adaptive α per round.",
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
            "rounds":                    rounds_total,
            "local_steps":               local_steps,
            "batch_size":                batch_size,
            "learning_rate":             learning_rate,
            "eval_interval":             eval_interval,
            "seed":                      seed,
            "measurement_noise_std":     noise_std,
            "selfadaptive_tau":          tau,
            "selfadaptive_delta":        delta
        },
        "algorithm": {
            "name":   "Self-Adaptive",
            "params": {"tau": tau, "delta": delta}
        },
        "timeline": timeline
    }

    # 5) Write to file
    folder = os.path.join("data", "experiment1")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "self-adaptive.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote static experiment data to {path}")

if __name__ == "__main__":
    generate_selfadaptive_json()
