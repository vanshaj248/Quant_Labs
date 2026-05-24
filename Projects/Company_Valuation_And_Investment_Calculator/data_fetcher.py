"""
Data Fetcher: Alpaca (price/market data) + Finnhub (financials)
"""
import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

ALPACA_KEY    = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET = os.getenv("ALPACA_SECRET_KEY", "")
FINNHUB_KEY   = os.getenv("FINNHUB_API_KEY", "")

ALPACA_BASE  = "https://data.alpaca.markets/v2"
ALPACA_TRADE = "https://api.alpaca.markets/v2"
FINNHUB_BASE = "https://finnhub.io/api/v1"


def _alpaca_headers():
    return {
        "APCA-API-KEY-ID": ALPACA_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
    }


def _fh(endpoint: str, params: dict) -> dict:
    params["token"] = FINNHUB_KEY
    r = requests.get(f"{FINNHUB_BASE}/{endpoint}", params=params, timeout=15)
    r.raise_for_status()
    return r.json()


# ── Alpaca ────────────────────────────────────────────────────────────────────

def get_latest_quote(symbol: str) -> dict:
    """Latest trade price from Alpaca."""
    url = f"{ALPACA_BASE}/stocks/{symbol}/trades/latest"
    r = requests.get(url, headers=_alpaca_headers(), timeout=10)
    if r.status_code == 200:
        data = r.json()
        trade = data.get("trade", {})
        return {
            "price": trade.get("p", 0),
            "size":  trade.get("s", 0),
            "time":  trade.get("t", ""),
        }
    return {"price": 0, "size": 0, "time": ""}


def get_historical_bars(symbol: str, days: int = 365) -> list:
    """Daily OHLCV bars for past N days."""
    end   = datetime.utcnow()
    start = end - timedelta(days=days)
    url   = f"{ALPACA_BASE}/stocks/{symbol}/bars"
    params = {
        "timeframe": "1Day",
        "start":     start.strftime("%Y-%m-%dT00:00:00Z"),
        "end":       end.strftime("%Y-%m-%dT00:00:00Z"),
        "limit":     1000,
        "feed":      "iex",
    }
    r = requests.get(url, headers=_alpaca_headers(), params=params, timeout=15)
    if r.status_code == 200:
        return r.json().get("bars", [])
    return []


def get_asset_info(symbol: str) -> dict:
    """Basic asset metadata from Alpaca."""
    url = f"{ALPACA_TRADE}/assets/{symbol}"
    r = requests.get(url, headers=_alpaca_headers(), timeout=10)
    if r.status_code == 200:
        return r.json()
    return {}


# ── Finnhub ───────────────────────────────────────────────────────────────────

def get_company_profile(symbol: str) -> dict:
    try:
        return _fh("stock/profile2", {"symbol": symbol})
    except Exception:
        return {}


def get_basic_financials(symbol: str) -> dict:
    try:
        return _fh("stock/metric", {"symbol": symbol, "metric": "all"})
    except Exception:
        return {}


def get_income_statement(symbol: str) -> dict:
    try:
        return _fh("financials-reported", {
            "symbol": symbol,
            "freq": "annual",
        })
    except Exception:
        return {}


def get_earnings(symbol: str) -> dict:
    try:
        return _fh("stock/earnings", {"symbol": symbol, "limit": 8})
    except Exception:
        return {}


def get_peers(symbol: str) -> list:
    try:
        data = _fh("stock/peers", {"symbol": symbol})
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_dividends(symbol: str) -> list:
    try:
        end   = datetime.utcnow().strftime("%Y-%m-%d")
        start = (datetime.utcnow() - timedelta(days=5*365)).strftime("%Y-%m-%d")
        data  = _fh("stock/dividend", {
            "symbol": symbol,
            "from":   start,
            "to":     end,
        })
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_recommendation_trends(symbol: str) -> list:
    try:
        data = _fh("stock/recommendation", {"symbol": symbol})
        return data if isinstance(data, list) else []
    except Exception:
        return []


def get_news_sentiment(symbol: str) -> dict:
    try:
        return _fh("news-sentiment", {"symbol": symbol})
    except Exception:
        return {}


def get_financials_as_reported(symbol: str) -> dict:
    """Fetch balance sheet / income / CF data."""
    try:
        return _fh("financials", {
            "symbol":    symbol,
            "statement": "cf",
            "freq":      "annual",
        })
    except Exception:
        return {}


def validate_keys() -> tuple[bool, str]:
    """Quick sanity-check on API keys."""
    errors = []
    if not ALPACA_KEY or ALPACA_KEY == "your_alpaca_api_key_here":
        errors.append("ALPACA_API_KEY missing")
    if not ALPACA_SECRET or ALPACA_SECRET == "your_alpaca_secret_key_here":
        errors.append("ALPACA_SECRET_KEY missing")
    if not FINNHUB_KEY or FINNHUB_KEY == "your_finnhub_api_key_here":
        errors.append("FINNHUB_API_KEY missing")
    return (len(errors) == 0, "; ".join(errors))
