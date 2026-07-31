# FinGuard AI — Real-Time Fraud Detection Platform

A full-stack fraud detection system that simulates card transactions, scores them for fraud risk in real time using a trained machine learning model, and explains *why* each transaction was flagged — built to mirror the kind of fraud detection infrastructure used at fintechs like Revolut.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## What it does

- **Simulates** thousands of realistic card transactions, including noisy, overlapping fraud patterns (not perfectly separable — mimicking real-world data)
- **Scores** any transaction for fraud risk in real time via a trained XGBoost model
- **Explains** every prediction using SHAP, showing exactly which features pushed a transaction toward — or away from — being flagged
- **Serves** everything through a REST API and a live analyst dashboard for browsing, filtering, and reviewing flagged transactions

---

## Demo

> 🎥 *[Add a link to your screen recording / GIF here once recorded]*

Run locally in under 2 minutes — see [Quickstart](#quickstart) below.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Dashboard  │────▶│   FastAPI    │────▶│  PostgreSQL │
│ (HTML/JS)   │◀────│   REST API   │◀────│ (transactions)│
└─────────────┘     └──────┬───────┘     └─────────────┘
                            │
                    ┌───────▼────────┐
                    │  XGBoost Model  │
                    │  + SHAP explain │
                    └────────────────┘
```

- **API layer**: FastAPI, serving both the REST endpoints and the static dashboard
- **Data layer**: PostgreSQL, managed with SQLAlchemy ORM and Alembic migrations
- **ML layer**: XGBoost classifier trained on engineered features (time-based, amount-based, risk-flag, and one-hot categorical), evaluated with precision/recall/ROC-AUC rather than accuracy alone (fraud is a rare-class problem — accuracy is misleading)
- **Explainability**: SHAP TreeExplainer, returning per-prediction feature impact scores
- **Simulation**: a custom transaction generator with intentional label noise, so the classification problem isn't trivially solvable by simple rules

---

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| ML | XGBoost, scikit-learn, pandas, SHAP |
| Frontend | Vanilla HTML/CSS/JS (no build step) |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Infrastructure | Docker, Docker Compose |

---

## Quickstart

**Requirements**: Docker Desktop installed and running.

```bash
git clone https://github.com/subhan-bit/FinGuard-AI.git
cd FinGuard-AI

# Copy environment variables
cp .env.example .env

# Build and start API + PostgreSQL
docker compose up --build -d

# Run database migrations
docker exec -it finguard-api alembic upgrade head

# Seed the database with realistic sample transactions
docker exec -it finguard-api python -m app.simulator.seed_database --count 8000 --fraud-rate 0.03

# Train the fraud detection model
docker exec -it finguard-api python -m app.ml.train
```

Then open **http://localhost:8000** for the dashboard, or **http://localhost:8000/docs** for the interactive API documentation.

---

## Running Locally (without Docker)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Start PostgreSQL via Docker (or point DATABASE_URL at your own instance)
docker compose up -d postgres

# Run migrations
alembic upgrade head

# Seed data and train the model
python -m app.simulator.seed_database --count 8000 --fraud-rate 0.03
python -m app.ml.train

# Start the API
uvicorn app.main:app --reload
```

---

## Running Tests

```bash
pytest -v
```

Tests cover three layers:
- **Feature engineering** — pure unit tests on the `build_features()` transformation logic
- **Fraud scoring** — sanity checks that the trained model scores obviously fraudulent/legitimate transactions correctly
- **API** — integration tests against live endpoints (health check, listing/filtering, scoring, 404 handling)

CI runs the full suite automatically on every push via GitHub Actions — see `.github/workflows/ci.yml`.

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/transactions` | List transactions with pagination and filters (fraud status, country, category, amount range, flagged status) |
| `GET` | `/transactions/{id}` | Retrieve a single transaction |
| `GET` | `/transactions/stats/summary` | Aggregate stats: total volume, fraud count, fraud rate, flagged count |
| `POST` | `/transactions/score` | Score a new transaction in real time, returns fraud probability, decision, and SHAP explanation |
| `GET` | `/health` | Health check |

Full interactive documentation available at `/docs` (Swagger UI).

---

## Model Performance

Evaluated on a held-out 20% test split:

| Metric | Legit Class | Fraud Class |
|---|---|---|
| Precision | 0.99 | 0.58 |
| Recall | 0.98 | 0.79 |
| F1-score | 0.99 | 0.67 |

**ROC-AUC: 0.97**

### A note on these numbers

An earlier version of this model scored a suspicious 100% precision/recall with a perfect 1.0 AUC. That's a red flag, not a win — it meant the synthetic fraud generator and the feature engineering were using the *same* underlying rules, so the model was trivially reverse-engineering the label logic rather than learning anything meaningful.

The generator was deliberately updated to inject label noise — some legitimate transactions now have "risky-looking" traits (e.g. a genuine 1am jewelry purchase), and some fraud is generated to look more subtle. The result is a lower, but far more honest and realistic, set of metrics — and a natural talking point about the precision/recall tradeoff: in production, the classification threshold would be tuned based on the real cost of a false positive (annoyed customer, declined card) versus a false negative (missed fraud).

---

## Project Structure

```
FinGuard-AI/
├── app/
│   ├── api/            # FastAPI route handlers
│   ├── db/              # Database connection/session setup
│   ├── ml/               # Feature engineering, training script, saved model artifacts
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/        # Fraud scoring + SHAP explanation services
│   ├── simulator/        # Transaction data generator + DB seeding
│   ├── static/           # Dashboard frontend (HTML/CSS/JS)
│   └── main.py           # FastAPI app entrypoint
├── alembic/               # Database migrations
├── tests/                # Pytest test suite
├── .github/workflows/    # CI pipeline
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## What I'd Add With More Time

Being transparent about scope — these are natural next steps that weren't prioritized to keep this project focused:

- **Cloud deployment** — currently designed to run via `docker compose up` locally or on any VM; a managed deployment (ECS/Fargate, or a PaaS like Render/Railway) is a natural next step
- **Kafka streaming** — replacing the one-off scoring endpoint with a continuous simulated transaction stream, for true real-time throughput testing
- **Automated retraining / drift detection** — monitoring for feature or prediction drift over time and triggering retraining, closer to a production MLOps setup
- **Authentication** — the dashboard and API are currently open; a real deployment would need auth on both

---

## License

MIT
