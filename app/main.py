from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import transactions

app = FastAPI(
    title="FinGuard AI",
    description="Real-Time Fraud Detection Platform",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")