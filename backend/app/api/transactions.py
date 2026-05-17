from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.core.logger import get_logger
from app.models.user import User
from app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])
logger = get_logger(__name__)

@router.get("/")
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=100)
):
    offset = (page - 1) * limit
    total = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).count()

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    logger.info(f"User {current_user.email} fetched transactions page={page}")

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": -(-total // limit),
        "transactions": [
            {
                "id": str(t.id),
                "type": t.type,
                "coin": t.coin_symbol,
                "quantity": t.quantity,
                "price_at_time": t.price_at_time,
                "total_value": round(t.quantity * t.price_at_time, 2),
                "date": t.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for t in transactions
        ]
    }