"""
Data Ingestion Pipeline
Fetches Finnhub data and stores it in DuckDB
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent to path to import from test folder
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "test"))

try:
    import finnhub
    from finnhub_pipeline import (
        get_company_profile,
        get_quote,
        get_key_metrics,
        get_earnings
    )
except ImportError:
    finnhub = None

from src.database.init_db import CompanyDatabase


class FinancialDataIngestion:
    """Fetch financial data from Finnhub and ingest into DuckDB."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.api_key = api_key
        self.client = finnhub.Client(api_key=api_key) if finnhub else None
        self.db = CompanyDatabase()
    
    def ingest_company_data(self, ticker: str):
        """Fetch and ingest company data from Finnhub."""
        if not self.client:
            print("❌ Finnhub client not available")
            return False
        
        try:
            ticker = ticker.upper()
            print(f"\n📥 Ingesting data for {ticker}...")
            
            # Get company profile
            profile = get_company_profile(ticker, self.api_key)
            if not profile.empty:
                row = profile.iloc[0]
                self.db.add_company(
                    ticker,
                    row.get('name', ticker),
                    sector=row.get('sector'),
                    industry=row.get('industry'),
                    country=row.get('country'),
                    website=row.get('website'),
                    description=row.get('description')
                )
                print(f"  ✓ Company profile added")
            
            # Get current quote
            quote = get_quote(ticker, self.api_key)
            if not quote.empty:
                current_price = quote.iloc[0].get('c')
                print(f"  ✓ Current price: ${current_price:.2f}")
            
            # Get key metrics
            metrics = get_key_metrics(ticker, self.api_key)
            if not metrics.empty:
                metric = metrics.iloc[0]
                # Extract latest year financials (simplified)
                print(f"  ✓ Key metrics loaded")
            
            # Get earnings
            earnings = get_earnings(ticker, self.client)
            if not earnings.empty:
                print(f"  ✓ Earnings data loaded ({len(earnings)} records)")
            
            return True
        
        except Exception as e:
            print(f"  ❌ Error ingesting {ticker}: {e}")
            return False
    
    def ingest_multiple(self, tickers: list):
        """Ingest data for multiple companies."""
        print(f"\n{'='*60}")
        print(f"  Multi-Company Data Ingestion")
        print(f"{'='*60}")
        
        for ticker in tickers:
            self.ingest_company_data(ticker)
        
        print(f"\n✓ Ingestion complete\n")
    
    def close(self):
        """Close database connection."""
        self.db.close()


def load_api_key_from_env() -> str:
    """Load API key from .env file."""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("FINNHUB_API_KEY"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    
    return os.getenv("FINNHUB_API_KEY", "")
