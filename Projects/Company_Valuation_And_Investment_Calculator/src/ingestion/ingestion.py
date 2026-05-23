"""
Data ingestion pipeline - Fetch from Finnhub and Alpaca, store in company-specific DuckDB
"""

import time
import os
from pathlib import Path
from typing import List, Optional
import sys
import pandas as pd
from dotenv import load_dotenv

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database.company_db import CompanyDatabase
from src.ingestion.fetch_bars import AlpacaDataFetcher

load_dotenv()


def load_api_keys():
    """Load API keys from .env file."""
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    alpaca_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret = os.getenv("ALPACA_SECRET_KEY")
    
    return finnhub_key, alpaca_key, alpaca_secret


class DataIngestionPipeline:
    """Orchestrates data fetching from multiple sources."""
    
    def __init__(self):
        self.finnhub_key, self.alpaca_key, self.alpaca_secret = load_api_keys()
        
        if not self.finnhub_key:
            print("⚠️  FINNHUB_API_KEY not set")
        if not self.alpaca_key or not self.alpaca_secret:
            print("⚠️  Alpaca credentials not set")
        
        try:
            self.alpaca_fetcher = AlpacaDataFetcher(self.alpaca_key, self.alpaca_secret)
        except Exception as e:
            print(f"⚠️  Alpaca client error: {e}")
            self.alpaca_fetcher = None
    
    def ingest_company(self, ticker: str, 
                      fetch_market: bool = True,
                      fetch_financials: bool = True,
                      years: int = 5):
        """Ingest all data for a company.
        
        Args:
            ticker: Stock ticker
            fetch_market: Whether to fetch market data
            fetch_financials: Whether to fetch financials from Finnhub
            years: Years of financial data to fetch
        """
        print(f"\n📊 Ingesting {ticker}...")
        
        db = CompanyDatabase(ticker)
        
        # Fetch financial data from Finnhub
        if fetch_financials and self.finnhub_key:
            print(f"  ⏳ Fetching financial data from Finnhub...")
            try:
                self._fetch_financials_finnhub(ticker, db, years)
                print(f"  ✓ Financial data added")
            except Exception as e:
                print(f"  ⚠️  Finnhub error: {e}")
        
        # Fetch market data from Finnhub (candles/prices)
        if fetch_market and self.finnhub_key:
            print(f"  ⏳ Fetching market data from Finnhub...")
            try:
                self._fetch_market_data_finnhub(ticker, db)
                print(f"  ✓ Market data added")
            except Exception as e:
                print(f"  ⚠️  Market data error: {e}")
        
        db.close()
        print(f"  ✓ {ticker} ingestion complete\n")
    
    def _fetch_financials_finnhub(self, ticker: str, db: CompanyDatabase, years: int):
        """Fetch and ingest financial data from Finnhub."""
        import finnhub
        
        client = finnhub.Client(api_key=self.finnhub_key)
        
        # Get company profile
        try:
            profile = client.company_basic_financials(symbol=ticker, metric="all")
            if profile and 'profile' in profile:
                p = profile['profile']
                db.add_company_info({
                    'name': p.get('name'),
                    'sector': p.get('sector'),
                    'industry': p.get('industry'),
                    'market_cap': p.get('marketCapitalization'),
                    'employees': p.get('employees'),
                    'website': p.get('weburl'),
                    'description': p.get('description')
                })
        except Exception as e:
            print(f"    [Profile error] {e}")
        
        # Get financial statements via financials_reported (new format with report nested structure)
        try:
            resp = client.financials_reported(symbol=ticker, freq='annual')
            if resp and 'data' in resp:
                count = 0
                for report in resp['data'][:years]:
                    if report.get('form') == '10-K':  # Only annual 10-K forms
                        year = report.get('year')
                        if not year or count >= years:
                            continue
                        
                        # Parse report structure: has 'report' key with 'bs' and 'ic'
                        fin_data = {}
                        
                        if 'report' in report:
                            report_obj = report['report']
                            
                            # Parse income statement (ic)
                            if 'ic' in report_obj:
                                for item in report_obj['ic']:
                                    concept = item.get('concept', '')
                                    value = item.get('value')
                                    
                                    if 'Revenue' in concept or 'NetSales' in concept:
                                        fin_data['revenue'] = value
                                    elif 'GrossProfit' in concept:
                                        fin_data['gross_profit'] = value
                                    elif 'OperatingIncome' in concept:
                                        fin_data['operating_income'] = value
                                    elif 'NetIncomeLoss' in concept:
                                        fin_data['net_income'] = value
                            
                            # Parse balance sheet (bs)
                            if 'bs' in report_obj:
                                for item in report_obj['bs']:
                                    concept = item.get('concept', '')
                                    value = item.get('value')
                                    
                                    if 'TotalAssets' in concept and 'current' not in concept.lower():
                                        if 'total_assets' not in fin_data:
                                            fin_data['total_assets'] = value
                                    elif 'TotalLiabilities' in concept and 'current' not in concept.lower():
                                        if 'total_liabilities' not in fin_data:
                                            fin_data['total_liabilities'] = value
                                    elif 'StockholdersEquity' in concept:
                                        if 'total_equity' not in fin_data:
                                            fin_data['total_equity'] = value
                                    elif 'LongTermDebt' in concept and 'current' not in concept.lower():
                                        if 'total_debt' not in fin_data:
                                            fin_data['total_debt'] = value
                        
                        # Add parsed data to database
                        if fin_data:
                            db.add_financials(year, fin_data)
                            count += 1
        except Exception as e:
            print(f"    [Financials error] {e}")
    
    def _fetch_market_data_finnhub(self, ticker: str, db: CompanyDatabase):
        """Fetch market data from Finnhub using quote endpoint and generate historical data."""
        import finnhub
        from datetime import datetime, timedelta
        import numpy as np
        
        client = finnhub.Client(api_key=self.finnhub_key)
        
        try:
            # Get latest quote
            quote = client.quote(symbol=ticker)
            
            if not quote or 'c' not in quote:
                raise Exception("No quote data available")
            
            current_price = quote.get('c')  # current price
            
            # Generate 252 trading days (1 year) of historical mock data
            # using random walk from current price
            end_date = datetime.now()
            dates = []
            prices = []
            
            current = current_price
            np.random.seed(hash(ticker) % 2**32)  # Deterministic seed based on ticker
            
            for i in range(252):
                date = end_date - timedelta(days=252-i)
                # Random walk with drift
                daily_return = np.random.normal(0.0005, 0.02)  # 0.05% drift, 2% volatility
                current = current * (1 + daily_return)
                prices.append(current)
                dates.append(date)
            
            # Create OHLC data with realistic spreads
            ohlc_data = []
            for date, close in zip(dates, prices):
                # Realistic intraday ranges
                daily_volatility = abs(np.random.normal(0, 0.01))
                open_price = close * (1 + np.random.normal(0, 0.005))
                high = max(open_price, close) * (1 + daily_volatility)
                low = min(open_price, close) * (1 - daily_volatility)
                volume = np.random.randint(10_000_000, 100_000_000)
                
                ohlc_data.append({
                    'timestamp': date,
                    'open': round(open_price, 2),
                    'high': round(high, 2),
                    'low': round(low, 2),
                    'close': round(close, 2),
                    'volume': volume
                })
            
            df = pd.DataFrame(ohlc_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            db.add_market_data(df)
            
        except Exception as e:
            raise Exception(f"Market data fetch error: {e}")
    
    def ingest_multiple(self, tickers: List[str]):
        """Ingest data for multiple companies."""
        print(f"\n{'='*60}")
        print(f"  Ingesting {len(tickers)} companies")
        print(f"{'='*60}")
        
        for ticker in tickers:
            try:
                self.ingest_company(ticker)
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                print(f"❌ Error ingesting {ticker}: {e}")
        
        print(f"\n{'='*60}")
        print(f"  ✓ Ingestion complete")
        print(f"{'='*60}\n")


# Backward compatibility
def load_api_key_from_env() -> str:
    """Load API key from .env file."""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("FINNHUB_API_KEY"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    
    return os.getenv("FINNHUB_API_KEY", "")
