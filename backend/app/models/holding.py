from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.db import Base
from datetime import datetime
import uuid

class Holding(Base):
    __tablename__ = "holdings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    coin_symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    buy_price_usd = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)