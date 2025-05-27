# FedAdapt

> **FedAdapt** extends [FedScale](https://fedscale.readthedocs.io/en/latest/index.html)  
> with a live Dashboard, Self-Adaptive Personalization, and  
> Heterogeneity-Aware Co-Optimization.


┌──────────────────────┐   REST / gRPC   ┌─────────────────────────┐
│ Dashboard Backend    │◀──────────────▶│  FedScale Aggregator &  │
│  (FastAPI / Uvicorn) │                │      Executors          │
└──────────────────────┘                └─────────────────────────┘
│ HTTP / SSE
▼
┌──────────────────────┐
│ Dashboard Frontend   │
│    (React + Vite)    │
└──────────────────────┘


---

## 📄 Research Paper

Dive into the full design, theory, and experiments in our [FedAdapt Research Paper](assets/paper.pdf) (PDF).

---

## 🚀 Overview & Motivation

Federated Learning (FL) allows training across many clients without centralizing their data, but real-world deployments face three key challenges:

1. **Statistical heterogeneity**  
   Clients collect data under wildly different distributions, slowing convergence and biasing the global model.

2. **System heterogeneity**  
   Devices vary in compute power, network bandwidth, and availability, creating stragglers and wasted work.

3. **Observability gaps**  
   Practitioners lack real-time dashboards to debug and monitor FL rounds, making tuning and deployment painful.

**FedAdapt** addresses all three with:

- **Live Dashboard** for end-to-end monitoring  
- **Self-Adaptive Personalization** that dynamically blends local/global models per client  
- **Heterogeneity-Aware Co-Optimization** that tunes each client's local-step count & compression  

---

## 🧭 Site Navigation

1. **Dashboard**  
   See how to launch experiments, stream real-time metrics, and visualize global & per-client charts.  
   👉 [dashboard.md](dashboard.md)

2. **Self-Adaptive Personalization**  
   Learn how each client adaptively mixes its local and global weights for better per-user accuracy.  
   👉 [self_adaptive.md](self_adaptive.md)

3. **Heterogeneity-Aware Co-Optimization**  
   Discover how we solve a tiny per-client grid-search each round to minimize compute + communication time.  
   👉 [cooptimization.md](cooptimization.md)

---

## ⚡ Quick Start

```bash
git clone https://github.com/YourUser/FedAdapt.git
cd FedAdapt
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

```
```
