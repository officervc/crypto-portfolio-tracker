# Crypto Portfolio Tracker

A full stack cryptocurrency portfolio tracker built with FastAPI and vanilla JavaScript.

## What it does
- User registration and login with JWT authentication
- Live cryptocurrency prices from CoinGecko API (BTC, ETH, BNB, SOL, XRP)
- Portfolio tracking with real-time profit/loss and ROI calculation
- 7-day price history charts for each coin
- Paginated transaction history
- Partial holding removal

## Tech Stack
**Backend:** Python, FastAPI, PostgreSQL, SQLAlchemy, JWT, bcrypt  
**Frontend:** HTML, CSS, Vanilla JavaScript  
**External API:** CoinGecko (free tier)

## Why these choices
- **FastAPI over Flask** — built-in Pydantic validation + auto Swagger docs at /docs
- **PostgreSQL over SQLite** — production-grade, handles concurrent users
- **UUID primary keys** — prevents enumeration attacks
- **JWT authentication** — stateless, scales without session storage
- **bcrypt** — one-way password hashing, safe even if DB is compromised
- **Rate limiting** — 5 register / 10 login attempts per minute per IP
- **Pagination** — transaction history stays fast regardless of data size

## How to run

**Backend**
cd C:\Users\USER\Desktop\crypto_portfolio\backend
uvicorn app.main:app --reload
(Press CTRL+C to quit)

**Frontend**
cd C:\Users\USER\Desktop\crypto_portfolio\backend
python -m http.server 5500
(Press CTRL+C to quit)

Open http://localhost:5500/login.html

API docs at http://localhost:8000/docs

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create account |
| POST | /auth/login | Get JWT token |
| GET | /prices/ | Live crypto prices |
| GET | /prices/history/{symbol} | 7-day price history |
| POST | /portfolio/add | Add a holding |
| GET | /portfolio/ | View portfolio with P&L |
| DELETE | /portfolio/remove/{id} | Remove holding (partial supported) |
| GET | /transactions/ | Paginated transaction history |
