#!/usr/bin/env python3
"""
Finnhub Pipeline CLI
Usage:
    python run.py AAPL
    python run.py AAPL --price-from 2019-01-01
    python run.py MSFT GOOGL TSLA --json
"""

import argparse
import os
import sys
from pathlib import Path
from finnhub_pipeline import run_pipeline, print_summary

# Load API key from .env file if it exists
def load_env():
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line.startswith("FINNHUB_API_KEY"):
                    key = line.split("=")[1].strip().strip('"').strip("'")
                    os.environ["FINNHUB_API_KEY"] = key
                    break

load_env()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch financial data from Finnhub API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py AAPL
  python run.py MSFT --price-from 2019-01-01
  python run.py AAPL GOOGL TSLA --no-excel --json
        """
    )
    parser.add_argument("tickers", nargs="+", help="One or more stock ticker symbols (e.g. AAPL MSFT)")
    parser.add_argument("--api-key", default=os.getenv("FINNHUB_API_KEY"), help="Finnhub API key (or set FINNHUB_API_KEY env var)")
    parser.add_argument("--price-from", default="2020-01-01", help="Start date for price history (default: 2020-01-01)")
    parser.add_argument("--no-excel", action="store_true", help="Skip saving Excel file")
    parser.add_argument("--json", action="store_true", help="Also save JSON file")
    parser.add_argument("--summary", action="store_true", default=True, help="Print a summary table (default: True)")
    parser.add_argument("--no-summary", dest="summary", action="store_false")

    args = parser.parse_args()

    # ── API key check ──────────────────────────────────────────────────────────
    if not args.api_key:
        print("\n❌  No API key found.")
        print("   Set it via:  export FINNHUB_API_KEY=your_key_here")
        print("   Or pass:     --api-key your_key_here\n")
        sys.exit(1)

    # ── Run pipeline for each ticker ──────────────────────────────────────────
    for ticker in args.tickers:
        results = run_pipeline(
            ticker=ticker,
            api_key=args.api_key,
            save_excel=not args.no_excel,
            save_json=args.json,
            price_from=args.price_from,
        )
        if args.summary:
            print_summary(results)


if __name__ == "__main__":
    main()