from sqlalchemy import Column, String, Float, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from datetime import datetime
import uuid
import enum

class TransactionType(str, enum.Enum):
    add = "add"
    remove = "remove"
    sell = "sell"

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    coin_symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price_at_time = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)