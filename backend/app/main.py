from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.db import Base, engine
from app.core.errors import register_error_handlers
from app.core.rate_limit import limiter
from app.core.logger import get_logger
from app.api import auth, portfolio, prices, transactions
import app.models

Base.metadata.create_all(bind=engine)

logger = get_logger(__name__)

app = FastAPI(title="Crypto Portfolio Tracker")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth.router)
app.include_router(prices.router)
app.include_router(portfolio.router)
app.include_router(transactions.router)

@app.get("/")
def root():
    return {"message": "Crypto Portfolio API is running"}

@app.on_event("startup")
async def startup():
    logger.info("Crypto Portfolio API started")