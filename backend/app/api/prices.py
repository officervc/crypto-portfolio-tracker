from fastapi import APIRouter
from app.services.price_service import fetch_prices
import httpx

router = APIRouter(prefix="/prices", tags=["prices"])

COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple"
}

@router.get("/")
async def get_prices():
    prices = await fetch_prices()
    if not prices:
        return {"error": "Could not fetch prices, try again shortly"}
    return prices

@router.get("/history/{symbol}")
async def get_price_history(symbol: str):
    coin_id = COINGECKO_IDS.get(symbol.upper())
    if not coin_id:
        return {"error": "Unsupported coin"}
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(
                f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": "7"},
                timeout=10
            )
            data = res.json()
            prices = data.get("prices", [])
            return {
                "symbol": symbol.upper(),
                "labels": [
                    __import__('datetime').datetime.fromtimestamp(p[0]/1000).strftime("%b %d")
                    for p in prices[::24]
                ],
                "prices": [round(p[1], 2) for p in prices[::24]]
            }
    except Exception:
        return {"error": "Could not fetch history"}