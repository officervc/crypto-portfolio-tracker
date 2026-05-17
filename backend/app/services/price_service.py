import httpx

SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT"
}

_price_cache = {}

async def fetch_prices() -> dict:
    global _price_cache
    try:
        async with httpx.AsyncClient() as client:
            prices = {}
            for symbol, pair in SYMBOLS.items():
                response = await client.get(
                    f"https://api.binance.com/api/v3/ticker/price",
                    params={"symbol": pair},
                    timeout=10
                )
                data = response.json()
                prices[symbol] = float(data["price"])
            _price_cache = prices
            return prices
    except Exception:
        return _price_cache if _price_cache else {}