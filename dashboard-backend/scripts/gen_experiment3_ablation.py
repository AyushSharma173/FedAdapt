#!/usr/bin/env python3
import os
import json
import numpy as np

def logistic_curve(rounds, k, x0, y0, y_max):
    """Generate a logistic growth curve."""
    return y0 + (y_max - y0) / (1 + np.exp(-k * (rounds - x0)))

def generate_ablation_jsons():
    # --- Experiment settings (shared) ---
    exp_name       = "experiment3"
    num_clients    = 100
    rounds_total   = 200
    eval_interval  = 10
    seed_base      = 42
    noise_std      = 0.01
    partition_alpha= 0.5

    # the 3×3 grid of (τ, Δ)
    thresholds = [0.01, 0.02, 0.05]
    steps      = [0.05, 0.10, 0.20]

    out_folder = os.path.join("data", exp_name)
    os.makedirs(out_folder, exist_ok=True)

    rounds = np.arange(0, rounds_total + 1)

    for tau in thresholds:
        for delta in steps:
            tid, sid = int(tau*100), int(delta*100)
            variant  = f"t{tid}s{sid}"  # e.g. "t1s5"
            path     = os.path.join(out_folder, f"{variant}.json")

            # --- derive global‐accuracy logistic parameters from ablation paper ---
            k   = 0.05 - 0.015 * (tau / 0.02) - 0.005 * abs(delta - 0.10) / 0.10
            x0  = 85   + 10    * (tau / 0.05) +  2   * abs(delta - 0.10) / 0.10
            y0, y_max = 0.10, 0.72

            # build a noisy global-accuracy curve
            rng = np.random.RandomState(seed_base + tid + sid)
            base  = logistic_curve(rounds, k, x0, y0, y_max)
            noise = rng.normal(scale=noise_std, size=rounds.shape)
            global_curve = np.clip(base + noise, y0, y_max)
            for _ in range(8):  # occasional dips/spikes
                i = rng.randint(50, 180)
                perturb = rng.choice([-1, 1]) * rng.uniform(0.01, 0.03)
                global_curve[i:i+2] = np.clip(global_curve[i:i+2] + perturb, y0, y_max)

            # initialize all client alphas to 0.5
            alphas = np.full(num_clients, 0.5, dtype=float)

            # --- build timeline events ---
            timeline = [{
                "type": "status",
                "round": 0,
                "running": True,
                "virtual_clock": 0.0,
                "sampled_clients": list(range(num_clients))
            }]

            for r in range(eval_interval, rounds_total + 1, eval_interval):
                g_acc = float(global_curve[r])
                clients = []
                for cid in range(num_clients):
                    # simulate local accuracy with noise around g_acc
                    local_acc = float(np.clip(
                        g_acc + rng.normal(scale=0.01), 0.0, 1.0
                    ))

                    # **self-adaptive α update** per your paper
                    diff = local_acc - g_acc
                    if diff >  tau:
                        alphas[cid] = min(alphas[cid] + delta, 1.0)
                    elif diff < -tau:
                        alphas[cid] = max(alphas[cid] - delta, 0.0)
                    # else α stays the same

                    # toy loss curve of length 10
                    loss_curve = [
                        float(np.clip(1.0 - 0.05*step + rng.normal(scale=0.01), 0.0, 1.0))
                        for step in range(10)
                    ]

                    clients.append({
                        "id":                      cid,
                        "loss_curve":             loss_curve,
                        "client_eval_local_acc":  local_acc,
                        "client_eval_global_acc": g_acc,
                        "client_alpha":          float(alphas[cid])
                    })

                timeline.append({
                    "type":    "metrics",
                    "round":   r,
                    "top1":    g_acc,
                    "top5":    g_acc,
                    "clients": clients
                })

            timeline.append({
                "type": "status",
                "round": rounds_total,
                "running": False,
                "virtual_clock": float(rounds_total),
                "sampled_clients": list(range(num_clients))
            })

            # --- assemble JSON payload ---
            out = {
                "id":          variant,
                "name":        f"Ablation (τ={tau}, Δ={delta})",
                "description": "Self-Adaptive α-mixing ablation",
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
                    "rounds":               rounds_total,
                    "eval_interval":        eval_interval,
                    "seed":                 int(seed_base + tid + sid),
                    "measurement_noise_std": noise_std,
                    "selfadaptive_tau":     tau,
                    "selfadaptive_delta":   delta
                },
                "algorithm": {
                    "name":   "Self-Adaptive (ablation)",
                    "params": {"tau": tau, "step": delta}
                },
                "timeline": timeline
            }

            with open(path, "w") as f:
                json.dump(out, f, indent=2)
            print(f"Wrote {path}")

if __name__ == "__main__":
    generate_ablation_jsons()
