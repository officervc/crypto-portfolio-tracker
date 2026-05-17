from pydantic import BaseModel, field_validator
from uuid import UUID

SUPPORTED_COINS = ["BTC", "ETH", "BNB", "SOL", "XRP"]

class AddHoldingRequest(BaseModel):
    coin_symbol: str
    quantity: float
    buy_price_usd: float

    @field_validator("coin_symbol")
    @classmethod
    def validate_coin(cls, v):
        v = v.upper().strip()
        if v not in SUPPORTED_COINS:
            raise ValueError(f"Unsupported coin. Choose from: {', '.join(SUPPORTED_COINS)}")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        if v > 1_000_000:
            raise ValueError("Quantity too large")
        return v

    @field_validator("buy_price_usd")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Buy price must be greater than 0")
        if v > 10_000_000:
            raise ValueError("Buy price too large")
        return v

class HoldingResponse(BaseModel):
    id: UUID
    coin_symbol: str
    quantity: float
    buy_price_usd: float
    current_price: float
    current_value: float
    profit_loss: float
    profit_loss_pct: float

class PortfolioResponse(BaseModel):
    holdings: list[HoldingResponse]
    total_invested: float
    total_current_value: float
    total_profit_loss: float
    total_roi_pct: float
    best_performer: str | None
    worst_performer: str | None

class RemoveHoldingRequest(BaseModel):
    quantity: float

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than 0")
        return v