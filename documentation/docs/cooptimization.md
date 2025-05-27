<!-- ````markdown -->
# Heterogeneity-Aware Co-Optimization

> Dynamically tailor each client’s work (local steps & compression) to minimize per-round runtime.

---

## 🎯 Motivation

Real-world devices vary wildly in compute speed, network bandwidth, and availability.  
A fixed “one-size-fits-all” choice of local steps or gradient compression can:  
- Slow down overall wall-clock convergence (stragglers)  
- Waste bandwidth on fast clients  
- Under-utilize powerful devices  

**Heterogeneity-Aware Co-Optimization** automatically picks, _per client per round_, the best:
- **𝑘** = number of local SGD steps  
- **𝑐** = compression ratio on the model update  

to minimize  
\[
T_i(k,c) = k \cdot t_{\text{comp},i} \;+\; c \cdot B \cdot t_{\text{comm},i}
\]  
where each client’s compute & comm timings \((t_{\text{comp},i},t_{\text{comm},i})\) are profiled in-situ, and \(B\) is the model-update size.

---

## ⚙️ How It Works

Inside the **Aggregator**’s `round_completion_handler()`:

```python
# profile: per‐client compute & comm times
profiles = {
    client: {
      "t_step": comp_i,
      "t_comm": comm_i / model_bits
    }
    for client, (comp_i, comm_i) in profiled_times.items()
}

# grid search over k ∈ {1, default_steps}, c ∈ {1.0, 0.5, 0.25}
new_conf = {}
for client, prof in profiles.items():
    best = None
    for k in [1, args.local_steps]:
      for c in [1.0, 0.5, 0.25]:
        T = k * prof["t_step"] + c * model_bits * prof["t_comm"]
        if best is None or T < best[0]:
            best = (T, k, c)
    new_conf[client] = Namespace(
      local_steps=best[1],
      compression=best[2],
      batch_size=args.batch_size,
      # …other fields…
    )

self.client_conf = new_conf
<!-- ```` -->

Each client then sees its tuned `(k, c)` on the next `CLIENT_TRAIN` event.

---

## 🛠 Configuration

Expose three fields in your CLI/REST and dashboard:

| Flag / Form Field | Description | Default |
| ----------------- | ----------- | :-----: |
| `--optimize_for`  | Strategy:   |         |

* **Fastest Training**
* **Balanced**
* **Best Accuracy**            | `Balanced` |
  \| `--compression_limit`| Maximum allowed compression ratio `[0.1–1.0]`  | `1.0`      |
  \| `--auto_tune`        | Enable/disable automatic per-client tuning     | `True`     |

### Dashboard UI Snippet

<details>
<summary><strong>Heterogeneity-Aware Optimization (settings)</strong></summary>

```jsx
<fieldset>
  <legend>Heterogeneity-Aware Optimization</legend>

  <label>
    Optimize For:
    <select
      name="optimize_for"
      value={form.optimize_for}
      onChange={handleChange}
    >
      <option>Fastest Training</option>
      <option>Balanced</option>
      <option>Best Accuracy</option>
    </select>
  </label>

  <label>
    Compression Limit (cₘₐₓ):
    <input
      name="compression_limit"
      type="number" step="0.1" min="0.1" max="1.0"
      value={form.compression_limit}
      onChange={handleChange}
    />
  </label>

  <label>
    Auto Tune:
    <select
      name="auto_tune"
      value={form.auto_tune.toString()}
      onChange={e => setForm(f => ({ …f, auto_tune: e.target.value === 'true' }))}
    >
      <option value="true">Enabled</option>
      <option value="false">Disabled</option>
    </select>
  </label>
</fieldset>
```

</details>

---

## 📊 Visualizing Co-Optimization

On the dashboard you can plot per-client choices each round:

* **Local Steps (k)** vs **Round**
* **Compression Ratio (c)** vs **Round**
* **Bandwidth Saved** (baseline − actual)

![Co-Opt Metrics](assets/coopt-metrics.png)

> **Tip**:
>
> * Lower `compression_limit` forces more aggressive sparsification.
> * Disable `auto_tune` to use a single global `(k,c)` fallback.

---

## 🔧 Defaults & Tuning Tips

* **Balanced**: trades off compute vs. comm.
* **Fastest Training**: biases toward more local steps on fast clients.
* **Best Accuracy**: biases toward lower compression.
* If you care more about accuracy than speed, pick **Best Accuracy** and set `compression_limit` near 1.0.

---

## 🏗 Architecture

```text
┌──────────────────────┐      gRPC      ┌────────────────────┐
│  FastAPI / Uvicorn   │◀──────────────▶│  FedScale Aggregator│
│ (dashboard-backend)  │                │    & Executor      │
└──────────────────────┘                └────────────────────┘
         │                                    ▲
         │ HTTP / SSE                        │ Grid‐search (k,c)
         ▼                                    │ per‐client
┌──────────────────────┐                      │
│  React + Vite        │                      ▼
│ (dashboard-frontend) │                ┌────────────────────┐
└──────────────────────┘                │   Co-Optimizer     │
                                        │ (in Aggregator)    │
                                        └────────────────────┘
```

---

*Read more in [the research paper](https://arxiv.org/abs/…) or see the code in*
`fedscale/cloud/aggregation/aggregator.py → Aggregator.round_completion_handler()`

````
