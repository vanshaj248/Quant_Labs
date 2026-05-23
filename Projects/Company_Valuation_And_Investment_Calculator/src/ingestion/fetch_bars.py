"""
Alpaca data fetcher - Historical OHLCV data
"""

import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class AlpacaDataFetcher:
    """Fetch market data from Alpaca API."""
    
    def __init__(self, api_key: str = None, secret_key: str = None):
        """Initialize Alpaca client.
        
        Args:
            api_key: Alpaca API key (default: ALPACA_API_KEY env var)
            secret_key: Alpaca secret key (default: ALPACA_SECRET_KEY env var)
        """
        self.api_key = api_key or os.getenv("ALPACA_API_KEY")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        
        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials not found. Set ALPACA_API_KEY and ALPACA_SECRET_KEY env vars.")
        
        self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
    
    def get_historical_data(self, ticker: str, 
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None,
                           timeframe: str = "daily") -> pd.DataFrame:
        """Fetch historical OHLCV data.
        
        Args:
            ticker: Stock ticker
            start_date: Start date (YYYY-MM-DD), default: 1 year ago
            end_date: End date (YYYY-MM-DD), default: today
            timeframe: 'daily', 'hourly', 'minute'
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        
        # Default to 1 year of data
        if end_date is None:
            end_date = datetime.now()
        else:
            end_date = pd.to_datetime(end_date)
        
        if start_date is None:
            start_date = end_date - timedelta(days=365)
        else:
            start_date = pd.to_datetime(start_date)
        
        try:
            # Map timeframe string to TimeFrame enum (use capitalized names)
            tf_map = {
                'minute': TimeFrame.Minute,
                'hourly': TimeFrame.Hour,
                'daily': TimeFrame.Day
            }
            tf = tf_map.get(timeframe.lower(), TimeFrame.Day)
            
            # Create request
            request = StockBarsRequest(
                symbol_or_symbols=ticker,
                timeframe=tf,
                start=start_date,
                end=end_date
            )
            
            # Fetch bars
            bars = self.client.get_stock_bars(request)
            
            if not bars or ticker not in bars.data:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = bars.data[ticker]
            df = pd.DataFrame([{
                'timestamp': bar.timestamp,
                'open': bar.open,
                'high': bar.high,
                'low': bar.low,
                'close': bar.close,
                'volume': bar.volume
            } for bar in data])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            return df
        
        except Exception as e:
            print(f"Error fetching {ticker} data from Alpaca: {e}")
            return pd.DataFrame()
    
    def get_latest_quote(self, ticker: str) -> Optional[dict]:
        """Get latest quote data.
        
        Returns:
            Dict with: timestamp, open, high, low, close, volume
        """
        df = self.get_historical_data(ticker, start_date=datetime.now() - timedelta(days=1))
        
        if df.empty:
            return None
        
        latest = df.iloc[-1]
        return {
            'timestamp': latest['timestamp'],
            'open': latest['open'],
            'high': latest['high'],
            'low': latest['low'],
            'close': latest['close'],
            'volume': latest['volume']
        }

