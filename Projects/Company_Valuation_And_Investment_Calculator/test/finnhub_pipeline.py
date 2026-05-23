"""
Finnhub Data Pipeline
Fetches financial statements and company data for any ticker symbol.
"""

import os
import json
import time
import requests
import finnhub
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL = "https://finnhub.io/api/v1"
OUTPUT_DIR = Path("/Users/vanshaj/Work/GitHub/Quant_Labs/Projects/Company_Valuation_And_Investment_Calculator/test")
OUTPUT_DIR.mkdir(exist_ok=True)


# ── Core HTTP helper ──────────────────────────────────────────────────────────

def _get(endpoint: str, api_key: str, params: dict = None) -> dict | list | None:
    """Make a GET request to the Finnhub API and return parsed JSON."""
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params["token"] = api_key

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # Finnhub returns {"error": "..."} or similar on bad requests
        if isinstance(data, dict) and ("error" in data or "message" in data):
            err_msg = data.get("error") or data.get("message")
            print(f"  [API Error] {err_msg}")
            return None

        return data

    except requests.exceptions.HTTPError as e:
        print(f"  [HTTP {resp.status_code}] {e}")
    except requests.exceptions.RequestException as e:
        print(f"  [Request failed] {e}")
    except json.JSONDecodeError:
        print(f"  [Bad JSON] {resp.text[:200]}")

    return None


# ── Company / Profile ─────────────────────────────────────────────────────────

def get_company_profile(ticker: str, api_key: str) -> pd.DataFrame:
    """General company info: name, sector, market cap, description, etc."""
    data = _get("/stock/profile2", api_key, {"symbol": ticker})
    if not data:
        return pd.DataFrame()
    return pd.DataFrame([data])


def get_key_metrics(ticker: str, api_key: str) -> pd.DataFrame:
    """Key financial metrics (PE, Market Cap, etc.)."""
    data = _get("/stock/metric", api_key, {"symbol": ticker, "metric": "all"})
    if not data or "metric" not in data:
        return pd.DataFrame()
    # Flatten the metrics into a DataFrame
    metrics = data.get("metric", {})
    return pd.DataFrame([metrics])


def get_peers(ticker: str, api_key: str) -> list[str]:
    """List of peer/competitor tickers."""
    data = _get("/stock/peers", api_key, {"symbol": ticker})
    if not data or not isinstance(data, list):
        return []
    return data


# ── Financial Statements ──────────────────────────────────────────────────────

def get_financials(ticker: str, client: finnhub.Client, freq: str = "annual", limit: int = 5) -> pd.DataFrame:
    """
    Fetch financial statements using client.financials_reported().
    freq: 'annual' or 'quarterly'
    """
    try:
        response = client.financials_reported(symbol=ticker, freq=freq)
        if not response or "data" not in response:
            return pd.DataFrame()
        
        reports = response.get("data", [])
        if not reports:
            return pd.DataFrame()
        
        # Convert to DataFrame and return top limit records
        df = pd.DataFrame(reports[:limit])
        return df
    except Exception as e:
        print(f"    [Error fetching financials] {e}")
        return pd.DataFrame()


def get_income_statement(ticker: str, client: finnhub.Client) -> pd.DataFrame:
    """Income statement using client.financials_reported()."""
    return get_financials(ticker, client, freq="annual", limit=5)


def get_balance_sheet(ticker: str, client: finnhub.Client) -> pd.DataFrame:
    """Balance sheet using client.financials_reported()."""
    return get_financials(ticker, client, freq="annual", limit=5)


def get_cash_flow(ticker: str, client: finnhub.Client) -> pd.DataFrame:
    """Cash flow statement using client.financials_reported()."""
    return get_financials(ticker, client, freq="annual", limit=5)


def get_earnings(ticker: str, client: finnhub.Client, limit: int = 8) -> pd.DataFrame:
    """Earnings calendar using client."""
    try:
        # earnings_calendar requires date range parameters
        to_date = datetime.today().strftime("%Y-%m-%d")
        from_date = (datetime.today() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        response = client.earnings_calendar(**{
            'symbol': ticker,
            '_from': from_date,
            'to': to_date
        })
        if not response or "earningsCalendar" not in response:
            return pd.DataFrame()
        earnings = response.get("earningsCalendar", [])
        return pd.DataFrame(earnings[:limit])
    except Exception as e:
        print(f"    [Error fetching earnings] {e}")
        return pd.DataFrame()


# ── Market Data ───────────────────────────────────────────────────────────────

def get_quote(ticker: str, api_key: str) -> pd.DataFrame:
    """Real-time quote: price, change, volume, etc."""
    data = _get("/quote", api_key, {"symbol": ticker})
    if not data:
        return pd.DataFrame()
    return pd.DataFrame([data])


def get_price_history(ticker: str, api_key: str, from_date: str = "2020-01-01", to_date: str = None) -> pd.DataFrame:
    """Daily OHLCV price history. Note: May require premium subscription."""
    to_date = to_date or datetime.today().strftime("%Y-%m-%d")
    
    # Convert dates to Unix timestamps
    try:
        from_ts = int(datetime.strptime(from_date, "%Y-%m-%d").timestamp())
        to_ts = int(datetime.strptime(to_date, "%Y-%m-%d").timestamp())
    except ValueError:
        return pd.DataFrame()
    
    data = _get("/stock/candle", api_key, {
        "symbol": ticker,
        "resolution": "D",
        "from": from_ts,
        "to": to_ts
    })
    
    if not data or "c" not in data:
        return pd.DataFrame()
    
    # Check if we got status "ok"
    if data.get("s") != "ok":
        return pd.DataFrame()
    
    # Reconstruct OHLCV from Finnhub response
    df = pd.DataFrame({
        "date": pd.to_datetime(data.get("t", []), unit="s"),
        "open": data.get("o", []),
        "high": data.get("h", []),
        "low": data.get("l", []),
        "close": data.get("c", []),
        "volume": data.get("v", [])
    })
    
    return df.sort_values("date").reset_index(drop=True) if not df.empty else df


# ── Full Pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(
    ticker: str,
    api_key: str,
    save_excel: bool = True,
    save_json: bool = False,
    price_from: str = "2020-01-01",
) -> dict[str, pd.DataFrame]:
    """
    Run the full Finnhub pipeline for a given ticker.

    Returns a dict of DataFrames keyed by dataset name.
    Optionally saves results to Excel (one sheet per dataset) and/or JSON.
    """
    ticker = ticker.upper().strip()
    
    # Initialize Finnhub client
    client = finnhub.Client(api_key=api_key)
    
    print(f"\n{'='*55}")
    print(f"  Finnhub Pipeline  |  {ticker}")
    print(f"{'='*55}")

    datasets = {
        "profile":          lambda: get_company_profile(ticker, api_key),
        "quote":            lambda: get_quote(ticker, api_key),
        "income_statement": lambda: get_income_statement(ticker, client),
        "balance_sheet":    lambda: get_balance_sheet(ticker, client),
        "cash_flow":        lambda: get_cash_flow(ticker, client),
        "key_metrics":      lambda: get_key_metrics(ticker, api_key),
        "earnings":         lambda: get_earnings(ticker, client),
        "price_history":    lambda: get_price_history(ticker, api_key, price_from),
    }

    results: dict[str, pd.DataFrame] = {}

    for name, fetch_fn in datasets.items():
        print(f"  Fetching {name:<22}", end="", flush=True)
        df = fetch_fn()
        results[name] = df
        status = f"✓  {len(df)} rows" if not df.empty else "✗  no data"
        print(status)
        time.sleep(0.25)   # polite rate-limiting

    # ── Save outputs ──────────────────────────────────────────────────────────
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if save_excel:
        # Only save if we have at least one sheet with data
        sheets_with_data = {k: v for k, v in results.items() if not v.empty}
        if sheets_with_data:
            path = OUTPUT_DIR / f"{ticker}_{timestamp}.xlsx"
            with pd.ExcelWriter(path, engine="openpyxl") as writer:
                for sheet, df in sheets_with_data.items():
                    df.to_excel(writer, sheet_name=sheet[:31], index=False)
            print(f"\n  Saved Excel  → {path}")
        else:
            print(f"\n  ⚠ No data to save (all API calls failed)")

    if save_json:
        path = OUTPUT_DIR / f"{ticker}_{timestamp}.json"
        json_data = {k: v.to_dict(orient="records") for k, v in results.items()}
        path.write_text(json.dumps(json_data, indent=2, default=str))
        print(f"  Saved JSON   → {path}")

    print(f"{'='*55}\n")
    return results


# ── Quick summary printer ─────────────────────────────────────────────────────

def print_summary(results: dict[str, pd.DataFrame]) -> None:
    """Print a readable snapshot of key data."""

    def val(df: pd.DataFrame, col: str, row: int = 0, fmt: str = ","):
        try:
            v = df.iloc[row][col]
            if pd.isna(v):
                return "N/A"
            return f"{v:{fmt}}" if fmt else str(v)
        except (KeyError, IndexError, ValueError):
            return "N/A"

    p = results.get("profile", pd.DataFrame())
    q = results.get("quote", pd.DataFrame())
    km = results.get("key_metrics", pd.DataFrame())

    print("\n" + "─"*55)
    if not p.empty:
        print(f"  {val(p,'name',fmt='')}  ({val(p,'ticker',fmt='')})")
        print(f"  {val(p,'weburl',fmt='')}")
    print("─"*55)

    if not q.empty:
        print(f"  Price          : {val(q,'c',fmt='')}")
        print(f"  Change         : {val(q,'d',fmt='')}")
        print(f"  Change %       : {val(q,'dp',fmt='')}")
        print(f"  Volume         : {val(q,'v')}")

    if not km.empty:
        print(f"  P/E Ratio      : {val(km,'peNormalizedAnnual',fmt='')}")
        print(f"  Market Cap     : {val(km,'marketCapitalization')}")
        print(f"  52-wk High     : {val(km,'52WeekHigh',fmt='')}")
        print(f"  52-wk Low      : {val(km,'52WeekLow',fmt='')}")

    print("─"*55 + "\n")
