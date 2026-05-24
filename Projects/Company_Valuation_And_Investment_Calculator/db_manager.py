"""
DuckDB manager — one database file per company ticker.
"""
import os
import json
import duckdb
from pathlib import Path
from datetime import datetime

DB_DIR = Path(os.path.dirname(__file__)) / "databases"
DB_DIR.mkdir(exist_ok=True)


def _db_path(ticker: str) -> Path:
    return DB_DIR / f"{ticker.upper()}.duckdb"


def get_connection(ticker: str) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(_db_path(ticker)))


def init_company_db(ticker: str) -> None:
    """Create all tables for a company database."""
    con = get_connection(ticker)
    con.execute("""
        CREATE TABLE IF NOT EXISTS company_profile (
            ticker          VARCHAR PRIMARY KEY,
            name            VARCHAR,
            exchange        VARCHAR,
            currency        VARCHAR,
            country         VARCHAR,
            ipo_date        VARCHAR,
            market_cap      DOUBLE,
            shares_out      DOUBLE,
            sector          VARCHAR,
            industry        VARCHAR,
            logo            VARCHAR,
            fetched_at      TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            date            DATE,
            open            DOUBLE,
            high            DOUBLE,
            low             DOUBLE,
            close           DOUBLE,
            volume          BIGINT,
            PRIMARY KEY (date)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            period          VARCHAR PRIMARY KEY,
            revenue         DOUBLE,
            net_income      DOUBLE,
            ebitda          DOUBLE,
            free_cash_flow  DOUBLE,
            total_debt      DOUBLE,
            total_equity    DOUBLE,
            interest_exp    DOUBLE,
            capex           DOUBLE,
            op_cash_flow    DOUBLE,
            shares_out      DOUBLE,
            fetched_at      TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            key             VARCHAR PRIMARY KEY,
            value           DOUBLE,
            fetched_at      TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS valuation (
            run_id          VARCHAR PRIMARY KEY,
            wacc            DOUBLE,
            intrinsic_value DOUBLE,
            market_price    DOUBLE,
            npv_project     DOUBLE,
            irr_project     DOUBLE,
            dcf_details     VARCHAR,  -- JSON blob
            computed_at     TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS dividends (
            ex_date         DATE,
            amount          DOUBLE,
            currency        VARCHAR,
            PRIMARY KEY (ex_date)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS peers (
            peer_ticker     VARCHAR PRIMARY KEY,
            fetched_at      TIMESTAMP DEFAULT current_timestamp
        )
    """)
    con.close()


def upsert_profile(ticker: str, profile: dict) -> None:
    con = get_connection(ticker)
    con.execute("""
        INSERT OR REPLACE INTO company_profile
            (ticker, name, exchange, currency, country, ipo_date,
             market_cap, shares_out, sector, industry, logo, fetched_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,current_timestamp)
    """, [
        ticker.upper(),
        profile.get("name", ""),
        profile.get("exchange", ""),
        profile.get("currency", "USD"),
        profile.get("country", ""),
        profile.get("ipo", ""),
        profile.get("marketCapitalization", 0) * 1e6,
        profile.get("shareOutstanding", 0) * 1e6,
        profile.get("finnhubIndustry", ""),
        profile.get("finnhubIndustry", ""),
        profile.get("logo", ""),
    ])
    con.close()


def upsert_price_history(ticker: str, bars: list) -> None:
    if not bars:
        return
    con = get_connection(ticker)
    for b in bars:
        t = b.get("t", "")[:10]
        con.execute("""
            INSERT OR REPLACE INTO price_history (date, open, high, low, close, volume)
            VALUES (?,?,?,?,?,?)
        """, [t, b.get("o",0), b.get("h",0), b.get("l",0),
              b.get("c",0), b.get("v",0)])
    con.close()


def upsert_metrics(ticker: str, metrics_dict: dict) -> None:
    con = get_connection(ticker)
    for k, v in metrics_dict.items():
        if isinstance(v, (int, float)):
            con.execute("""
                INSERT OR REPLACE INTO metrics (key, value, fetched_at)
                VALUES (?,?,current_timestamp)
            """, [k, float(v)])
    con.close()


def upsert_financials(ticker: str, rows: list[dict]) -> None:
    """rows: list of dicts with standardised keys."""
    con = get_connection(ticker)
    for r in rows:
        con.execute("""
            INSERT OR REPLACE INTO financials
                (period, revenue, net_income, ebitda, free_cash_flow,
                 total_debt, total_equity, interest_exp, capex, op_cash_flow,
                 shares_out, fetched_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,current_timestamp)
        """, [
            r.get("period",""),
            r.get("revenue", 0),
            r.get("net_income", 0),
            r.get("ebitda", 0),
            r.get("free_cash_flow", 0),
            r.get("total_debt", 0),
            r.get("total_equity", 0),
            r.get("interest_exp", 0),
            r.get("capex", 0),
            r.get("op_cash_flow", 0),
            r.get("shares_out", 0),
        ])
    con.close()


def upsert_dividends(ticker: str, divs: list) -> None:
    con = get_connection(ticker)
    for d in divs:
        try:
            con.execute("""
                INSERT OR REPLACE INTO dividends (ex_date, amount, currency)
                VALUES (?,?,?)
            """, [d.get("exDate",""), d.get("amount",0), d.get("currency","USD")])
        except Exception:
            pass
    con.close()


def upsert_peers(ticker: str, peers: list) -> None:
    con = get_connection(ticker)
    con.execute("DELETE FROM peers")
    for p in peers:
        if p and p != ticker.upper():
            con.execute("INSERT OR REPLACE INTO peers (peer_ticker, fetched_at) VALUES (?,current_timestamp)", [p])
    con.close()


def save_valuation(ticker: str, result: dict) -> None:
    con = get_connection(ticker)
    run_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    con.execute("""
        INSERT OR REPLACE INTO valuation
            (run_id, wacc, intrinsic_value, market_price, npv_project,
             irr_project, dcf_details, computed_at)
        VALUES (?,?,?,?,?,?,?,current_timestamp)
    """, [
        run_id,
        result.get("wacc", 0),
        result.get("intrinsic_value", 0),
        result.get("market_price", 0),
        result.get("npv_project", 0),
        result.get("irr_project", 0),
        json.dumps(result.get("dcf_details", {})),
    ])
    con.close()


def get_latest_financials(ticker: str) -> list[dict]:
    con = get_connection(ticker)
    try:
        rows = con.execute("""
            SELECT period, revenue, net_income, ebitda, free_cash_flow,
                   total_debt, total_equity, interest_exp, capex, op_cash_flow, shares_out
            FROM financials ORDER BY period DESC LIMIT 5
        """).fetchall()
        cols = ["period","revenue","net_income","ebitda","free_cash_flow",
                "total_debt","total_equity","interest_exp","capex","op_cash_flow","shares_out"]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        con.close()


def get_price_history(ticker: str, limit: int = 252) -> list[dict]:
    con = get_connection(ticker)
    try:
        rows = con.execute(f"""
            SELECT date, open, high, low, close, volume
            FROM price_history ORDER BY date DESC LIMIT {limit}
        """).fetchall()
        return [{"date": str(r[0]), "open": r[1], "high": r[2],
                 "low": r[3], "close": r[4], "volume": r[5]}
                for r in reversed(rows)]
    finally:
        con.close()


def get_metric(ticker: str, key: str) -> float:
    con = get_connection(ticker)
    try:
        row = con.execute("SELECT value FROM metrics WHERE key=?", [key]).fetchone()
        return row[0] if row else 0.0
    finally:
        con.close()


def get_all_metrics(ticker: str) -> dict:
    con = get_connection(ticker)
    try:
        rows = con.execute("SELECT key, value FROM metrics").fetchall()
        return {r[0]: r[1] for r in rows}
    finally:
        con.close()


def get_profile(ticker: str) -> dict:
    con = get_connection(ticker)
    try:
        row = con.execute("SELECT * FROM company_profile WHERE ticker=?", [ticker.upper()]).fetchone()
        if row:
            cols = ["ticker","name","exchange","currency","country","ipo_date",
                    "market_cap","shares_out","sector","industry","logo","fetched_at"]
            return dict(zip(cols, row))
        return {}
    finally:
        con.close()


def get_dividends_history(ticker: str) -> list[dict]:
    con = get_connection(ticker)
    try:
        rows = con.execute("SELECT ex_date, amount, currency FROM dividends ORDER BY ex_date DESC LIMIT 20").fetchall()
        return [{"ex_date": str(r[0]), "amount": r[1], "currency": r[2]} for r in rows]
    finally:
        con.close()


def get_peers_list(ticker: str) -> list:
    con = get_connection(ticker)
    try:
        rows = con.execute("SELECT peer_ticker FROM peers").fetchall()
        return [r[0] for r in rows]
    finally:
        con.close()


def get_latest_valuation(ticker: str) -> dict:
    con = get_connection(ticker)
    try:
        row = con.execute("""
            SELECT wacc, intrinsic_value, market_price, npv_project, irr_project, dcf_details, computed_at
            FROM valuation ORDER BY computed_at DESC LIMIT 1
        """).fetchone()
        if row:
            return {
                "wacc": row[0], "intrinsic_value": row[1], "market_price": row[2],
                "npv_project": row[3], "irr_project": row[4],
                "dcf_details": json.loads(row[5] or "{}"),
                "computed_at": str(row[6]),
            }
        return {}
    finally:
        con.close()


def list_companies() -> list[str]:
    """Return all tickers that have a database file."""
    return [f.stem for f in sorted(DB_DIR.glob("*.duckdb"))]
