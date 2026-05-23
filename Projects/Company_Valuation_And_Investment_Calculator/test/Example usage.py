"""
example_usage.py  –  Demonstrates how to use finnhub_pipeline programmatically.
Run this after:  pip install -r requirements.txt
"""

import os
from finnhub_pipeline import (
    run_pipeline,
    print_summary,
    get_income_statement,
    get_balance_sheet,
    get_cash_flow,
    get_company_profile,
    get_key_metrics,
    get_price_history,
    get_peers,
)

# ── Set your API key ──────────────────────────────────────────────────────────
# Option 1: environment variable (recommended)
#   export FINNHUB_API_KEY=your_key_here
#
# Option 2: hardcode (for quick local tests only — don't commit to git!)
API_KEY = "d88c5lpr01qq4342i490d88c5lpr01qq4342i49g"

#API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_API_KEY_HERE")
TICKER  = "AAPL"   # ← change this to any ticker


# ── Example 1: Run the full pipeline (saves Excel automatically) ──────────────
results = run_pipeline(
    ticker=TICKER,
    api_key=API_KEY,
    save_excel=True,
    save_json=False,
    price_from="2020-01-01",
)

# Print a quick summary
print_summary(results)


# ── Example 2: Access individual DataFrames ───────────────────────────────────
income  = results["income_statement"]
balance = results["balance_sheet"]
cashflow = results["cash_flow"]
profile  = results["profile"]
metrics  = results["key_metrics"]
prices   = results["price_history"]

# Useful columns from income statement
print("\n── Revenue trend ──")
print(income[["date", "revenue", "grossProfit", "netIncome", "epsdiluted"]].to_string(index=False))

print("\n── Balance sheet snapshot ──")
print(balance[["date", "totalAssets", "totalLiabilities", "totalStockholdersEquity", "totalDebt"]].to_string(index=False))

print("\n── Free cash flow ──")
print(cashflow[["date", "operatingCashFlow", "capitalExpenditure", "freeCashFlow"]].to_string(index=False))


# ── Example 3: Fetch a single dataset on demand ───────────────────────────────
peers = get_peers(TICKER, API_KEY)
print(f"\n── Peers of {TICKER}: {peers}")


# ── Example 4: Compare multiple tickers ───────────────────────────────────────
tickers = ["AAPL", "MSFT", "GOOGL"]
comparison_rows = []

for t in tickers:
    km = get_key_metrics(t, API_KEY, period="annual", limit=1)
    if not km.empty:
        row = km.iloc[0][["symbol", "peRatio", "debtToEquity", "roe", "freeCashFlowYield"]]
        comparison_rows.append(row)

import pandas as pd
if comparison_rows:
    comparison = pd.DataFrame(comparison_rows).reset_index(drop=True)
    print("\n── Multi-ticker comparison ──")
    print(comparison.to_string(index=False))