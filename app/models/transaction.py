import uuid
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    card_id = Column(String, index=True, nullable=False)
    merchant = Column(String, nullable=False)
    merchant_category = Column(String, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    country = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    is_fraud = Column(Boolean, default=False)          
    fraud_score = Column(Float, nullable=True)          
    predicted_fraud = Column(Boolean, nullable=True)    
    flagged = Column(Boolean, default=False)            

    created_at = Column(DateTime(timezone=True), server_default=func.now())