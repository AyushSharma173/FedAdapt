<!-- ````markdown -->
# Self-Adaptive Personalization

> Dynamically blend each client’s local and global model per round to mitigate non-IID drift.

---

## 🎯 Motivation

Federated Learning on non-IID data can bias the global model toward dominant shards.  
**Self-Adaptive Personalization** lets each client maintain both:
- a **local** model updated on its own data  
- the **global** model received from the server  

Each round, the client automatically adjusts a mixing weight **α∈[0,1]** to favor whichever model currently performs better on held-out data.

---

## ⚙️ How It Works

1. **Evaluate** both models on the client’s validation split:
   ```python
   local_acc  = self.evaluate_model(self.local_weights)
   global_acc = self.evaluate_model(self.global_weights)
<!-- ```` -->

2. **Adjust** the mixing weight α by threshold τ and step Δ:

   ```python
   if local_acc - global_acc > τ:
       self.alpha = min(self.alpha + Δ, 1.0)
   elif global_acc - local_acc > τ:
       self.alpha = max(self.alpha - Δ, 0.0)
   ```
3. **Mix** the weights before training:

   ```python
   mixed = [
     self.alpha * lw + (1 - self.alpha) * gw
     for lw, gw in zip(self.local_weights, self.global_weights)
   ]
   self.model_adapter.set_weights(mixed, is_aggregator=False)
   ```
4. **Train** with standard local SGD on `mixed`, then store updated weights in `self.local_weights`.

---

## 🛠 Configuration

Expose two hyperparameters in both **CLI/REST** and the dashboard UI:

| Flag / Form Field   | Description                     | Default |
| ------------------- | ------------------------------- | :-----: |
| `--alpha_threshold` | τ: min accuracy gap to adjust α |   0.02  |
| `--alpha_step`      | Δ: step size for α adjustments  |   0.10  |

### Dashboard UI Snippet

<details>
<summary><strong>Self-Adaptive Personalization (settings)</strong></summary>

```jsx
<fieldset>
  <legend>Self-Adaptive Personalization</legend>
  <label>
    α-threshold (τ):
    <input
      name="alpha_threshold"
      type="number" step="0.005" min="0" max="1"
      value={form.alpha_threshold}
      onChange={handleChange}
    />
  </label>
  <label>
    α-step (Δ):
    <input
      name="alpha_step"
      type="number" step="0.01" min="0" max="1"
      value={form.alpha_step}
      onChange={handleChange}
    />
  </label>
</fieldset>
```

</details>

![Self-Adaptive Settings](assets/self-adaptive-settings.png)

---

## 📊 Visualizing Personalization

Your dashboard can chart each client’s α over rounds:

![Alpha Trajectories](assets/alpha-trajectories.png)

> **Tip**: Higher τ/Δ makes α more conservative (slower to adapt).
> To push for stronger personalization, lower τ or increase Δ.

---

## 🔧 Defaults & Tuning Tips

* **Defaults**:

  * τ = **0.02**, Δ = **0.10** (empirically stable for CIFAR-10, Dirichlet α=0.5)
* **More personalization**:

  * **Lower τ** → more frequent α updates
  * **Increase Δ** → larger jumps in α per round
* **Less personalization**: do the opposite (higher τ, smaller Δ)

---

## 🏗 Architecture

```text
┌──────────────────────┐      gRPC      ┌────────────────────┐
│  FastAPI / Uvicorn   │◀──────────────▶│  FedScale Aggregator│
│ (dashboard-backend)  │                │    & Executor      │
└──────────────────────┘                └────────────────────┘
         │                                    ▲
         │ HTTP / SSE                        │ Evaluate + Mix
         ▼                                    │ Adjust α
┌──────────────────────┐                      │ Train on mixed weights
│  React + Vite        │                      │
│ (dashboard-frontend) │                      │
└──────────────────────┘                      ▼
                                      ┌────────────────────┐
                                      │   Local Client     │
                                      │(self-adaptive logic)│
                                      └────────────────────┘
```

1. **Dashboard/API**: user sets τ, Δ
2. **Executor**: each round → evaluate local vs global → adjust α → mix → train
3. **Aggregator**: standard FL orchestration + streams metrics

---

*Read more about the math and implementation in [the research paper](http://paper.fedadapt.com.s3-website.us-east-2.amazonaws.com/) or see the code in*
`fedscale/cloud/execution/executor.py → Executor.Train()`

```
```
