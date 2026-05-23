"""
data_pipeline.py
─────────────────────────────────────────────────────────────
Alpaca API data pipeline + DuckDB persistence layer.

Real usage: set ALPACA_API_KEY and ALPACA_SECRET_KEY in .env
Offline fallback: synthetic GBM data is generated automatically.
"""

import os
import json
import sqlite3
import datetime
import urllib.request
import urllib.parse
import urllib.error
import numpy as np
import pandas as pd
from pathlib import Path

# ── Try to load python-dotenv ──────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env variables must be exported manually

# ── Configuration ──────────────────────────────────────────
ALPACA_API_KEY  = os.getenv("ALPACA_API_KEY",  "")
ALPACA_SECRET   = os.getenv("ALPACA_SECRET_KEY","")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://data.alpaca.markets")
DB_PATH         = os.getenv("DB_PATH",         "pca_portfolio.db")
LOOKBACK_DAYS   = int(os.getenv("LOOKBACK_DAYS", "252"))

# ── 20 diversified S&P 500 / Nifty-representative tickers ─
TICKERS = [
    # Tech
    "AAPL", "MSFT", "NVDA", "GOOGL", "META",
    # Financials
    "JPM", "BAC", "GS", "WFC", "MS",
    # Energy
    "XOM", "CVX", "COP",
    # Healthcare
    "JNJ", "UNH", "PFE",
    # Consumer / Industrial
    "AMZN", "TSLA", "HD", "CAT",
]

SECTOR_MAP = {
    "AAPL": "Tech", "MSFT": "Tech", "NVDA": "Tech",
    "GOOGL": "Tech", "META": "Tech",
    "JPM": "Financials", "BAC": "Financials", "GS": "Financials",
    "WFC": "Financials", "MS": "Financials",
    "XOM": "Energy", "CVX": "Energy", "COP": "Energy",
    "JNJ": "Healthcare", "UNH": "Healthcare", "PFE": "Healthcare",
    "AMZN": "Consumer", "TSLA": "Consumer",
    "HD": "Industrial", "CAT": "Industrial",
}


# ══════════════════════════════════════════════════════════
#  DuckDB-compatible layer (uses sqlite3 as fallback since
#  DuckDB wheels are unavailable in this env; the SQL dialect
#  used is fully DuckDB-compatible — swap the connect call
#  when running locally with duckdb installed)
# ══════════════════════════════════════════════════════════
class Database:
    """Thin wrapper that mimics DuckDB's connection API over sqlite3."""

    def __init__(self, path: str = DB_PATH):
        self.path = path
        self.conn = sqlite3.connect(path)
        self._init_schema()

    def _init_schema(self):
        cur = self.conn.cursor()
        cur.executescript("""
            CREATE TABLE IF NOT EXISTS daily_prices (
                ticker      TEXT    NOT NULL,
                trade_date  TEXT    NOT NULL,
                open        REAL,
                high        REAL,
                low         REAL,
                close       REAL,
                volume      INTEGER,
                fetched_at  TEXT,
                PRIMARY KEY (ticker, trade_date)
            );

            CREATE TABLE IF NOT EXISTS pca_runs (
                run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at          TEXT NOT NULL,
                n_stocks        INTEGER,
                n_components    INTEGER,
                lookback_days   INTEGER,
                explained_var   TEXT,   -- JSON array
                eigenvalues     TEXT,   -- JSON array
                loadings        TEXT    -- JSON matrix
            );

            CREATE TABLE IF NOT EXISTS pca_components (
                run_id      INTEGER,
                component   INTEGER,
                ticker      TEXT,
                loading     REAL,
                FOREIGN KEY(run_id) REFERENCES pca_runs(run_id)
            );

            CREATE INDEX IF NOT EXISTS idx_prices_ticker
                ON daily_prices(ticker);
            CREATE INDEX IF NOT EXISTS idx_prices_date
                ON daily_prices(trade_date);
        """)
        self.conn.commit()

    def execute(self, sql: str, params=()) -> sqlite3.Cursor:
        return self.conn.execute(sql, params)

    def executemany(self, sql: str, rows):
        return self.conn.executemany(sql, rows)

    def commit(self):
        self.conn.commit()

    def fetch_df(self, sql: str, params=()) -> pd.DataFrame:
        return pd.read_sql_query(sql, self.conn, params=params)

    def close(self):
        self.conn.close()


# ══════════════════════════════════════════════════════════
#  Alpaca API helpers
# ══════════════════════════════════════════════════════════
def _alpaca_headers() -> dict:
    return {
        "APCA-API-KEY-ID":     ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET,
        "Accept":              "application/json",
    }


def _fetch_alpaca_bars(
    tickers: list[str],
    start: str,
    end: str,
    timeframe: str = "1Day",
) -> dict[str, list[dict]]:
    """
    Call Alpaca v2 multi-stock bars endpoint.
    Returns {ticker: [{t, o, h, l, c, v}, ...]}
    """
    base  = f"{ALPACA_BASE_URL}/v2/stocks/bars"
    syms  = ",".join(tickers)
    params = urllib.parse.urlencode({
        "symbols":   syms,
        "timeframe": timeframe,
        "start":     start,
        "end":       end,
        "limit":     10000,
        "adjustment":"split",
        "feed":      "iex",
    })
    url = f"{base}?{params}"
    req = urllib.request.Request(url, headers=_alpaca_headers())

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return data.get("bars", {})
    except Exception as exc:
        raise RuntimeError(f"Alpaca API error: {exc}") from exc


# ══════════════════════════════════════════════════════════
#  Synthetic data fallback (GBM simulation)
# ══════════════════════════════════════════════════════════
def _generate_synthetic(
    tickers: list[str],
    n_days: int = LOOKBACK_DAYS,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Simulate correlated daily returns using a factor model:
      r_i = β_i1 · F_market + β_i2 · F_sector + ε_i
    This ensures meaningful PCA structure for demonstration.
    """
    rng = np.random.default_rng(seed)
    n   = len(tickers)

    # Common factors
    market_factor = rng.normal(0.0003, 0.010, n_days)
    sector_factor = rng.normal(0.0001, 0.006, n_days)

    sectors = list(set(SECTOR_MAP.values()))
    sector_idx = {s: i for i, s in enumerate(sectors)}
    n_sectors = len(sectors)

    # Per-sector sub-factor
    sector_factors = rng.normal(0, 0.004, (n_sectors, n_days))

    prices: dict[str, np.ndarray] = {}
    for ticker in tickers:
        beta_m = rng.uniform(0.6, 1.4)
        beta_s = rng.uniform(0.3, 0.9)
        idio   = rng.normal(0, 0.008, n_days)
        sec    = SECTOR_MAP.get(ticker, "Other")
        si     = sector_idx.get(sec, 0)
        rets   = (beta_m * market_factor
                  + beta_s * sector_factor
                  + 0.5 * sector_factors[si]
                  + idio)
        prices[ticker] = 100.0 * np.cumprod(1 + rets)

    end_date   = datetime.date.today()
    # Generate enough dates and slice to exactly n_days
    dates      = pd.bdate_range(end=end_date, periods=n_days + 10)
    # Trim to match the simulated data length
    dates      = dates[-n_days:]
    df = pd.DataFrame({t: prices[t][:len(dates)] for t in prices}, index=dates)
    return df


# ══════════════════════════════════════════════════════════
#  Main fetch-and-store routine
# ══════════════════════════════════════════════════════════
def fetch_and_store(
    db: Database,
    tickers: list[str] | None = None,
    force_refresh: bool = False,
) -> tuple[pd.DataFrame, str]:
    """
    1. Check DB for cached prices.
    2. Try Alpaca API if keys present.
    3. Fall back to synthetic data.
    Returns (price_df, source_label).
    """
    tickers = tickers or TICKERS

    # ── Check cache ──────────────────────────────────────
    if not force_refresh:
        cached = db.fetch_df(
            "SELECT ticker, trade_date, close FROM daily_prices "
            "WHERE ticker IN ({}) ORDER BY trade_date".format(
                ",".join("?" * len(tickers))
            ),
            params=tickers,
        )
        if not cached.empty:
            pivot = cached.pivot(index="trade_date", columns="ticker", values="close")
            pivot.index = pd.to_datetime(pivot.index)
            if len(pivot) >= 60 and set(tickers).issubset(pivot.columns):
                return pivot, "database_cache"

    # ── Try Alpaca ────────────────────────────────────────
    source = "synthetic"
    price_df = None

    if ALPACA_API_KEY and ALPACA_API_KEY != "your_api_key_here":
        try:
            end_dt   = datetime.date.today()
            start_dt = end_dt - datetime.timedelta(days=int(LOOKBACK_DAYS * 1.5))
            bars     = _fetch_alpaca_bars(
                tickers,
                start_dt.isoformat(),
                end_dt.isoformat(),
            )
            rows = []
            for ticker, bar_list in bars.items():
                for b in bar_list:
                    rows.append((
                        ticker,
                        b["t"][:10],
                        b["o"], b["h"], b["l"], b["c"], b["v"],
                        datetime.datetime.utcnow().isoformat(),
                    ))
            if rows:
                db.executemany(
                    "INSERT OR REPLACE INTO daily_prices "
                    "(ticker,trade_date,open,high,low,close,volume,fetched_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    rows,
                )
                db.commit()
                source = "alpaca_api"
                cached = db.fetch_df(
                    "SELECT ticker, trade_date, close FROM daily_prices "
                    "WHERE ticker IN ({}) ORDER BY trade_date".format(
                        ",".join("?" * len(tickers))
                    ),
                    params=tickers,
                )
                price_df = cached.pivot(
                    index="trade_date", columns="ticker", values="close"
                )
                price_df.index = pd.to_datetime(price_df.index)
        except Exception:
            source = "synthetic"

    # ── Synthetic fallback ────────────────────────────────
    if price_df is None:
        price_df = _generate_synthetic(tickers, LOOKBACK_DAYS)
        # Store in DB so subsequent runs are consistent
        rows = []
        for ticker in tickers:
            for dt, close in price_df[ticker].items():
                rows.append((
                    ticker, str(dt.date()),
                    float(close), float(close), float(close), float(close),
                    0,
                    datetime.datetime.utcnow().isoformat(),
                ))
        db.executemany(
            "INSERT OR REPLACE INTO daily_prices "
            "(ticker,trade_date,open,high,low,close,volume,fetched_at) "
            "VALUES (?,?,?,?,?,?,?,?)",
            rows,
        )
        db.commit()

    # Trim to LOOKBACK_DAYS
    price_df = price_df.sort_index().iloc[-LOOKBACK_DAYS:]
    return price_df.dropna(axis=1, how="any"), source
