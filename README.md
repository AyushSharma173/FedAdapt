# FedAdapt

[![FedAdapt Docs](https://img.shields.io/badge/docs-FedAdapt-blue)](https://youruser.github.io/FedAdapt)  
[![Research Paper](https://img.shields.io/badge/paper-PDF-orange)](documentation/docs/assets/paper.pdf)  

**FedAdapt** builds on [FedScale](https://fedscale.readthedocs.io/en/latest/) to deliver three production-ready extensions for Federated Learning:

- **Live Dashboard** for real-time monitoring and control  
- **Self-Adaptive Personalization** that dynamically blends local/global models per client  
- **Heterogeneity-Aware Co-Optimization** to pick each client’s best local-step & compression ratio  

---

## 🔗 Quick Links

- **FedScale** tutorial & API docs → https://fedscale.readthedocs.io/en/latest/  
- **FedAdapt Documentation** → https://youruser.github.io/FedAdapt  
- **Research Paper (PDF)** → [documentation/docs/assets/paper.pdf](documentation/docs/assets/paper.pdf)  

---

## 🚀 Quick Start

```bash
# 1. Clone FedAdapt (includes all FedScale code + our extensions)
git clone https://github.com/YourUser/FedAdapt.git
cd FedAdapt

# 2. Create and activate Python venv
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Dashboard Backend
cd dashboard-backend
uvicorn app.main:app --reload --port 8000

# 5. Launch Dashboard Frontend (in another shell)
cd ../dashboard-frontend
npm install
npm run dev

# 6. Open http://localhost:3000 in your browser

---

## 📑 Features

### 1. Live Dashboard

* **REST & SSE** endpoints (FastAPI) stream per-round metrics
* **React + D3** frontend shows global convergence, α-trajectories, straggler profiles, bandwidth savings
* Start/stop experiments, override parameters in real time

### 2. Self-Adaptive Personalization

* Each client maintains **local** & **global** model copies
* Computes

  ```
  w_mix = α · w_local + (1–α) · w_global
  ```
* Updates α each round based on hold-out performance (threshold τ, step Δ)

### 3. Heterogeneity-Aware Co-Optimization

* Aggregator profiles each client’s compute (t\_comp) & comm (t\_comm)
* Solves tiny per-client grid search over local‐steps k ∈ {1,…,K} and compression c ∈ {c₁,…,cₘ}
* Minimizes Tᵢ(k,c) = k·t\_comp + c·B·t\_comm, pushes (k\*,c\*) to each client

---

## 🗂 Repository Structure

```
FedAdapt/
├── README.md
├── dashboard-backend/      # FastAPI backend for live metrics & control
├── dashboard-frontend/     # React + Vite dashboard UI
├── fedscale/               # FedScale core code (aggregator, executor, utils…)
├── docs/                   # MkDocs site (index.md, dashboard.md, self_adaptive.md, cooptimization.md)
├── assets/
├── requirements.txt
└── setup.py
```

---

## 📚 Citation

If you use FedAdapt in your research, please cite:

```bibtex
@article{sharma2025_fedadapt,
  title   = {FedAdapt: A Production-Ready Adaptive Federated Learning Framework},
  author  = {Sharma, Ayush},
  journal = {arXiv preprint arXiv:2501.01234},
  year    = {2025}
}
```

and, for the underlying platform:

```bibtex
@inproceedings{fedscale-icml22,
  title={{FedScale}: Benchmarking Model and System Performance of Federated Learning at Scale},
  author={Lai, Fan and Dai, Yinwei and Singapuram, Sanjay S. and ...},
  booktitle={ICML},
  year={2022}
}
```

---

## 🤝 Contributing

FedAdapt builds on the [FedScale contributor guidelines](https://github.com/SymbioticLab/FedScale).
Feel free to submit issues or pull requests—please include unit tests and follow existing style.
Join our Slack community or open a GitHub issue if you have questions!

```
```
