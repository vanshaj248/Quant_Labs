from connection import get_connection

conn = get_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS live_prices (
    timestamp TIMESTAMP,
    ticker VARCHAR,
    price DOUBLE,
    volume DOUBLE
);
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS financials (
    ticker VARCHAR,
    year INTEGER,
    revenue DOUBLE,
    ebit DOUBLE,
    net_income DOUBLE,
    free_cash_flow DOUBLE,
    debt DOUBLE,
    cash DOUBLE,
    shares_outstanding DOUBLE
);
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS valuation_results (
    ticker VARCHAR,
    intrinsic_value DOUBLE,
    market_price DOUBLE,
    upside_pct DOUBLE,
    wacc DOUBLE
);
""")

print("Database initialized successfully!")