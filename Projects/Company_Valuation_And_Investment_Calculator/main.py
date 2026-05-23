#!/usr/bin/env python3
"""
DCF Valuation Analyzer - Main Entry Point
Multi-company database system with Alpaca market data and Finnhub financials
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.tui import run_tui
from src.ingestion.ingestion import DataIngestionPipeline
from src.database.company_db import CompanyDatabase
from dotenv import load_dotenv

load_dotenv()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="DCF Valuation Analyzer - Multi-company database system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Launch TUI
  python main.py --ingest AAPL MSFT      # Ingest data for companies
  python main.py --status                 # Show data status
  python main.py --list                   # List all companies
        """
    )
    
    parser.add_argument("--ingest", nargs="*", metavar="TICKER",
                       help="Ingest market data from Alpaca and financials from Finnhub")
    parser.add_argument("--status", action="store_true",
                       help="Show database status for all companies")
    parser.add_argument("--list", action="store_true",
                       help="List all available companies")
    parser.add_argument("--clean", action="store_true",
                       help="Remove all company databases")
    
    args = parser.parse_args()
    
    # Default: launch TUI
    if not any([args.ingest is not None, args.status, args.list, args.clean]):
        print("\n" + "="*70)
        print("  DCF VALUATION ANALYZER - Multi-Company Database System")
        print("="*70 + "\n")
        run_tui()
        return
    
    # Handle --list
    if args.list:
        companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "BRK.B", "JPM", "V"
        ]
        print(f"\nAvailable companies ({len(companies)}):")
        for ticker in companies:
            print(f"  • {ticker}")
        print()
        return
    
    # Handle --status
    if args.status:
        companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "BRK.B", "JPM", "V"
        ]
        print(f"\n{'='*70}")
        print("  DATABASE STATUS")
        print(f"{'='*70}\n")
        print(f"{'Ticker':<10} {'Market Data':<15} {'Latest Price':<15} {'Financials':<15}")
        print("-"*70)
        
        for ticker in companies:
            db = CompanyDatabase(ticker)
            price = db.get_current_price()
            price_str = f"${price:.2f}" if price else "N/A"
            
            market_df = db.get_market_data(limit=1)
            market_status = f"✓ {len(market_df)} records" if not market_df.empty else "Empty"
            
            fin_df = db.get_latest_financials(years=1)
            fin_status = f"✓ {len(fin_df)} years" if not fin_df.empty else "Empty"
            
            print(f"{ticker:<10} {market_status:<15} {price_str:<15} {fin_status:<15}")
            db.close()
        
        print(f"\n{'='*70}\n")
        return
    
    # Handle --clean
    if args.clean:
        data_dir = Path(__file__).parent / "data" / "companies"
        if data_dir.exists():
            import shutil
            shutil.rmtree(data_dir)
            print("\n✓ All company databases removed\n")
        else:
            print("\nNo databases to clean\n")
        return
    
    # Handle --ingest
    if args.ingest is not None:
        tickers = args.ingest if args.ingest else [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"
        ]
        
        pipeline = DataIngestionPipeline()
        pipeline.ingest_multiple(tickers)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

