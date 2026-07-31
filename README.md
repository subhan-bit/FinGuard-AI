# FinGuard AI
Real-time fraud detection platform simulating card transactions, scoring fraud risk with ML, and explaining flagged transactions.

## Stack
FastAPI, PostgreSQL, Kafka, Redis, XGBoost/LightGBM, SHAP, Docker

## Status
In active development

## Setup

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
