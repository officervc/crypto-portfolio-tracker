from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.core.logger import get_logger
from app.models.user import User
from app.models.holding import Holding
from app.models.transaction import Transaction, TransactionType
from app.schemas.portfolio import AddHoldingRequest, RemoveHoldingRequest, PortfolioResponse, HoldingResponse
from app.services.price_service import fetch_prices
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/portfolio", tags=["portfolio"])
logger = get_logger(__name__)

@router.post("/add")
async def add_holding(
    data: AddHoldingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    holding = Holding(
        user_id=current_user.id,
        coin_symbol=data.coin_symbol,
        quantity=data.quantity,
        buy_price_usd=data.buy_price_usd
    )
    db.add(holding)

    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.add,
        coin_symbol=data.coin_symbol,
        quantity=data.quantity,
        price_at_time=data.buy_price_usd
    )
    db.add(transaction)
    db.commit()

    logger.info(f"User {current_user.email} added {data.quantity} {data.coin_symbol} at ${data.buy_price_usd}")
    return {"message": f"Added {data.quantity} {data.coin_symbol} to portfolio"}


@router.get("/", response_model=PortfolioResponse)
async def get_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    holdings = db.query(Holding).filter(Holding.user_id == current_user.id).all()
    prices = await fetch_prices()

    result = []
    total_invested = 0
    total_current_value = 0
    best = None
    worst = None

    for h in holdings:
        current_price = prices.get(h.coin_symbol, h.buy_price_usd)
        invested = h.quantity * h.buy_price_usd
        current_value = h.quantity * current_price
        profit_loss = current_value - invested
        profit_loss_pct = ((current_value - invested) / invested) * 100 if invested else 0

        if best is None or profit_loss_pct > best[1]:
            best = (h.coin_symbol, profit_loss_pct)
        if worst is None or profit_loss_pct < worst[1]:
            worst = (h.coin_symbol, profit_loss_pct)

        result.append(HoldingResponse(
            id=h.id,
            coin_symbol=h.coin_symbol,
            quantity=h.quantity,
            buy_price_usd=h.buy_price_usd,
            current_price=current_price,
            current_value=round(current_value, 2),
            profit_loss=round(profit_loss, 2),
            profit_loss_pct=round(profit_loss_pct, 2)
        ))

        total_invested += invested
        total_current_value += current_value

    total_roi_pct = ((total_current_value - total_invested) / total_invested * 100) if total_invested else 0

    logger.info(f"User {current_user.email} viewed portfolio - {len(result)} holdings")

    return PortfolioResponse(
        holdings=result,
        total_invested=round(total_invested, 2),
        total_current_value=round(total_current_value, 2),
        total_profit_loss=round(total_current_value - total_invested, 2),
        total_roi_pct=round(total_roi_pct, 2),
        best_performer=best[0] if best else None,
        worst_performer=worst[0] if worst else None
    )


@router.delete("/remove/{holding_id}")
def remove_holding(
    holding_id: str,
    data: RemoveHoldingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uid = uuid.UUID(holding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid holding ID format")

    holding = db.query(Holding).filter(
        Holding.id == uid,
        Holding.user_id == current_user.id
    ).first()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if data.quantity > holding.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"You only have {holding.quantity} {holding.coin_symbol}"
        )

    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.remove,
        coin_symbol=holding.coin_symbol,
        quantity=data.quantity,
        price_at_time=holding.buy_price_usd
    )
    db.add(transaction)

    if data.quantity == holding.quantity:
        db.delete(holding)
    else:
        holding.quantity -= data.quantity

    db.commit()
    logger.info(f"User {current_user.email} removed {data.quantity} {holding.coin_symbol}")
    return {"message": f"Removed {data.quantity} {holding.coin_symbol} from portfolio"}

class SellRequest(BaseModel):
    quantity: float

@router.post("/sell/{holding_id}")
async def sell_holding(
    holding_id: str,
    data: SellRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        uid = uuid.UUID(holding_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid holding ID format")

    holding = db.query(Holding).filter(
        Holding.id == uid,
        Holding.user_id == current_user.id
    ).first()

    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")

    if data.quantity > holding.quantity:
        raise HTTPException(status_code=400, detail=f"Max quantity is {holding.quantity}")

    prices = await fetch_prices()
    sell_price = prices.get(holding.coin_symbol, holding.buy_price_usd)

    transaction = Transaction(
        user_id=current_user.id,
        type=TransactionType.sell,
        coin_symbol=holding.coin_symbol,
        quantity=data.quantity,
        price_at_time=sell_price
    )
    db.add(transaction)

    if data.quantity == holding.quantity:
        db.delete(holding)
    else:
        holding.quantity -= data.quantity

    db.commit()

    logger.info(f"User {current_user.email} sold {data.quantity} {holding.coin_symbol} at ${sell_price}")
    return {"message": f"Sold {data.quantity} {holding.coin_symbol} at ${sell_price}"}