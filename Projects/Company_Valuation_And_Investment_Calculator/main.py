#!/usr/bin/env python3
"""
DCF Valuation Analyzer - Main Entry Point
Comprehensive company valuation with TVM, WACC, DCF, and NPV/IRR analysis
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database.init_db import CompanyDatabase, init_default_companies
from src.ingestion.ingestion import FinancialDataIngestion, load_api_key_from_env
from src.valuation_engine import CompanyValuationEngine, run_valuation
from src.tui import run_tui


def init_database():
    """Initialize database with default companies."""
    print("\n🗄️  Initializing DuckDB database...")
    init_default_companies()
    print("✓ Database ready\n")


def ingest_data(tickers: list = None):
    """Ingest financial data from Finnhub."""
    api_key = load_api_key_from_env()
    if not api_key:
        print("❌ Error: FINNHUB_API_KEY not found in .env file")
        return
    
    if tickers is None:
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"]
    
    ingestion = FinancialDataIngestion(api_key)
    ingestion.ingest_multiple(tickers)
    ingestion.close()


def run_single_valuation(ticker: str):
    """Run DCF valuation for a single company."""
    api_key = load_api_key_from_env()
    run_valuation(ticker, api_key)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DCF Valuation Analyzer - Comprehensive company valuation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run TUI
  python main.py --init             # Initialize database
  python main.py --ingest           # Ingest Top 5 companies
  python main.py --valuate AAPL     # Run DCF for Apple
  python main.py --ingest AAPL MSFT # Ingest specific companies
        """
    )
    
    parser.add_argument("--init", action="store_true", 
                       help="Initialize DuckDB database")
    parser.add_argument("--ingest", nargs="*",
                       help="Ingest data from Finnhub (optionally specify tickers)")
    parser.add_argument("--valuate", metavar="TICKER",
                       help="Run DCF valuation for a company")
    
    args = parser.parse_args()
    
    # If no args, run TUI
    if len(sys.argv) == 1:
        print("\n" + "="*70)
        print("  DCF VALUATION ANALYZER")
        print("="*70)
        print("\nStarting TUI interface...\n")
        init_database()
        run_tui()
    
    elif args.init:
        init_database()
    
    elif args.ingest is not None:
        tickers = args.ingest if args.ingest else None
        ingest_data(tickers)
    
    elif args.valuate:
        run_single_valuation(args.valuate)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
