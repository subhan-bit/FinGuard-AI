import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    card_id: str
    merchant: str
    merchant_category: Optional[str] = None
    amount: float
    currency: str = "USD"
    country: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Schema for manually creating a transaction via the API."""
    pass


class TransactionResponse(TransactionBase):
    """Schema returned to the client."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    timestamp: datetime
    is_fraud: bool
    fraud_score: Optional[float] = None
    predicted_fraud: Optional[bool] = None
    flagged: bool


class TransactionListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[TransactionResponse]

class TransactionScoreRequest(BaseModel):
    card_id: str
    merchant: str
    merchant_category: str
    amount: float
    currency: str = "USD"
    country: str


class FeatureImpact(BaseModel):
    feature: str
    impact: float


class TransactionScoreResponse(BaseModel):
    fraud_score: float
    predicted_fraud: bool
    flagged: bool
    explanation: list[FeatureImpact]