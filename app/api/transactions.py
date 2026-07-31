import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse, TransactionListResponse

from datetime import datetime, timezone

from app.schemas.transaction import TransactionScoreRequest, TransactionScoreResponse
from app.services.fraud_scorer import score_transaction

from app.services.explainer import explain_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    card_id: Optional[str] = None,
    country: Optional[str] = None,
    merchant_category: Optional[str] = None,
    is_fraud: Optional[bool] = None,
    flagged: Optional[bool] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
):
    """
    List transactions with optional filters and pagination.
    """
    query = db.query(Transaction)

    if card_id:
        query = query.filter(Transaction.card_id == card_id)
    if country:
        query = query.filter(Transaction.country == country)
    if merchant_category:
        query = query.filter(Transaction.merchant_category == merchant_category)
    if is_fraud is not None:
        query = query.filter(Transaction.is_fraud == is_fraud)
    if flagged is not None:
        query = query.filter(Transaction.flagged == flagged)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount is not None:
        query = query.filter(Transaction.amount <= max_amount)

    total = query.count()

    results = (
        query.order_by(desc(Transaction.timestamp))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return TransactionListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=results,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single transaction by ID.
    """
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn


@router.get("/stats/summary")
def transaction_stats(db: Session = Depends(get_db)):
    """
    Quick summary stats — total transactions, fraud count, fraud rate.
    """
    total = db.query(Transaction).count()
    fraud_count = db.query(Transaction).filter(Transaction.is_fraud == True).count()  # noqa: E712
    flagged_count = db.query(Transaction).filter(Transaction.flagged == True).count()  # noqa: E712

    return {
        "total_transactions": total,
        "fraud_count": fraud_count,
        "fraud_rate_percent": round((fraud_count / total * 100), 2) if total else 0,
        "flagged_count": flagged_count,
    }

@router.post("/score", response_model=TransactionScoreResponse)
def score_new_transaction(payload: TransactionScoreRequest, db: Session = Depends(get_db)):
    """
    Score a new transaction for fraud risk in real time, explain the
    prediction using SHAP, and persist it to the database.
    """
    txn_dict = {
        "amount": payload.amount,
        "country": payload.country,
        "merchant_category": payload.merchant_category,
        "timestamp": datetime.now(timezone.utc),
    }

    result, X = score_transaction(txn_dict)
    explanation = explain_transaction(X)

    new_txn = Transaction(
        card_id=payload.card_id,
        merchant=payload.merchant,
        merchant_category=payload.merchant_category,
        amount=payload.amount,
        currency=payload.currency,
        country=payload.country,
        is_fraud=False,
        fraud_score=result["fraud_score"],
        predicted_fraud=result["predicted_fraud"],
        flagged=result["flagged"],
    )
    db.add(new_txn)
    db.commit()
    db.refresh(new_txn)

    return TransactionScoreResponse(**result, explanation=explanation)