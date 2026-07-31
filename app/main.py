from fastapi import FastAPI

from app.api import transactions

app = FastAPI(
    title="FinGuard AI",
    description="Real-Time Fraud Detection Platform",
    version="0.1.0"
)

app.include_router(transactions.router)


@app.get("/")
def root():
    return {"message": "FinGuard AI is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}