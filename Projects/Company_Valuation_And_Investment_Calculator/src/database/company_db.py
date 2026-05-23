"""
Per-company DuckDB database handler
Creates one database file per company with market data and financials
"""

import duckdb
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd


class CompanyDatabase:
    """Manages DuckDB database for a single company."""
    
    def __init__(self, ticker: str, data_dir: str = None):
        """Initialize database for a company.
        
        Args:
            ticker: Stock ticker (e.g., 'AAPL')
            data_dir: Directory to store database files (default: /data/companies)
        """
        self.ticker = ticker.upper()
        
        if data_dir is None:
            data_dir = Path(__file__).resolve().parent.parent.parent / "data" / "companies"
        else:
            data_dir = Path(data_dir)
        
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / f"{self.ticker}.duckdb"
        self.conn = duckdb.connect(str(self.db_path))
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        
        # Market data (OHLCV)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                timestamp TIMESTAMP NOT NULL,
                open DOUBLE NOT NULL,
                high DOUBLE NOT NULL,
                low DOUBLE NOT NULL,
                close DOUBLE NOT NULL,
                volume BIGINT NOT NULL,
                PRIMARY KEY(timestamp)
            )
        """)
        
        # Company profile
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS company_info (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR,
                sector VARCHAR,
                industry VARCHAR,
                market_cap DOUBLE,
                employees INTEGER,
                website VARCHAR,
                description TEXT,
                last_updated TIMESTAMP
            )
        """)
        
        # Financial statements (annual)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS financials (
                fiscal_year INTEGER NOT NULL,
                revenue DOUBLE,
                gross_profit DOUBLE,
                operating_income DOUBLE,
                net_income DOUBLE,
                ebitda DOUBLE,
                operating_cash_flow DOUBLE,
                free_cash_flow DOUBLE,
                capital_expenditure DOUBLE,
                total_assets DOUBLE,
                total_liabilities DOUBLE,
                total_equity DOUBLE,
                cash_and_equivalents DOUBLE,
                total_debt DOUBLE,
                interest_expense DOUBLE,
                shares_outstanding DOUBLE,
                book_value_per_share DOUBLE,
                eps DOUBLE,
                roe DOUBLE,
                roa DOUBLE,
                last_updated TIMESTAMP,
                PRIMARY KEY(fiscal_year)
            )
        """)
        
        # Key metrics
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                metric_date DATE NOT NULL,
                beta DOUBLE,
                pe_ratio DOUBLE,
                pb_ratio DOUBLE,
                dividend_yield DOUBLE,
                current_ratio DOUBLE,
                debt_to_equity DOUBLE,
                roe DOUBLE,
                roa DOUBLE,
                price DOUBLE,
                PRIMARY KEY(metric_date)
            )
        """)
        
        # Valuation results
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS valuations (
                valuation_date DATE NOT NULL,
                current_price DOUBLE,
                wacc DOUBLE,
                fcf_year1 DOUBLE,
                fcf_year2 DOUBLE,
                fcf_year3 DOUBLE,
                fcf_year4 DOUBLE,
                fcf_year5 DOUBLE,
                terminal_value DOUBLE,
                intrinsic_value_per_share DOUBLE,
                margin_of_safety DOUBLE,
                recommendation VARCHAR,
                wacc_breakdown JSON,
                dcf_breakdown JSON,
                PRIMARY KEY(valuation_date)
            )
        """)
    
    def add_market_data(self, df: pd.DataFrame):
        """Add market data (OHLCV).
        
        Args:
            df: DataFrame with columns: timestamp, open, high, low, close, volume
        """
        if df.empty:
            return
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Insert or replace
        self.conn.execute("""
            INSERT OR REPLACE INTO market_data 
            SELECT * FROM df
        """)
        self.conn.commit()
    
    def add_company_info(self, data: Dict):
        """Add company profile information."""
        self.conn.execute("""
            INSERT OR REPLACE INTO company_info 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            self.ticker,
            data.get('name'),
            data.get('sector'),
            data.get('industry'),
            data.get('market_cap'),
            data.get('employees'),
            data.get('website'),
            data.get('description'),
            datetime.now()
        ])
        self.conn.commit()
    
    def add_financials(self, fiscal_year: int, data: Dict):
        """Add financial data for a fiscal year."""
        self.conn.execute("""
            INSERT OR REPLACE INTO financials 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            fiscal_year,
            data.get('revenue'),
            data.get('gross_profit'),
            data.get('operating_income'),
            data.get('net_income'),
            data.get('ebitda'),
            data.get('operating_cash_flow'),
            data.get('free_cash_flow'),
            data.get('capital_expenditure'),
            data.get('total_assets'),
            data.get('total_liabilities'),
            data.get('total_equity'),
            data.get('cash_and_equivalents'),
            data.get('total_debt'),
            data.get('interest_expense'),
            data.get('shares_outstanding'),
            data.get('book_value_per_share'),
            data.get('eps'),
            data.get('roe'),
            data.get('roa'),
            datetime.now()
        ])
        self.conn.commit()
    
    def add_metrics(self, metric_date, data: Dict):
        """Add key metrics for a date."""
        self.conn.execute("""
            INSERT OR REPLACE INTO metrics 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            metric_date,
            data.get('beta'),
            data.get('pe_ratio'),
            data.get('pb_ratio'),
            data.get('dividend_yield'),
            data.get('current_ratio'),
            data.get('debt_to_equity'),
            data.get('roe'),
            data.get('roa'),
            data.get('price')
        ])
        self.conn.commit()
    
    def add_valuation(self, valuation_date, data: Dict):
        """Add DCF valuation results."""
        self.conn.execute("""
            INSERT OR REPLACE INTO valuations 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            valuation_date,
            data.get('current_price'),
            data.get('wacc'),
            data.get('fcf_year1'),
            data.get('fcf_year2'),
            data.get('fcf_year3'),
            data.get('fcf_year4'),
            data.get('fcf_year5'),
            data.get('terminal_value'),
            data.get('intrinsic_value_per_share'),
            data.get('margin_of_safety'),
            data.get('recommendation'),
            json.dumps(data.get('wacc_breakdown', {})),
            json.dumps(data.get('dcf_breakdown', {}))
        ])
        self.conn.commit()
    
    def get_market_data(self, limit: int = 252) -> pd.DataFrame:
        """Get recent market data (default 1 year)."""
        return self.conn.execute(f"""
            SELECT * FROM market_data 
            ORDER BY timestamp DESC 
            LIMIT {limit}
        """).df()
    
    def get_company_info(self) -> Dict:
        """Get company profile."""
        result = self.conn.execute("""
            SELECT * FROM company_info WHERE ticker = ?
        """, [self.ticker]).fetchall()
        
        if not result:
            return {}
        
        row = result[0]
        return {
            'ticker': row[0],
            'name': row[1],
            'sector': row[2],
            'industry': row[3],
            'market_cap': row[4],
            'employees': row[5],
            'website': row[6],
            'description': row[7],
            'last_updated': row[8]
        }
    
    def get_latest_financials(self, years: int = 5) -> pd.DataFrame:
        """Get recent financial data."""
        return self.conn.execute(f"""
            SELECT * FROM financials 
            ORDER BY fiscal_year DESC 
            LIMIT {years}
        """).df()
    
    def get_latest_valuation(self) -> Optional[Dict]:
        """Get most recent DCF valuation."""
        result = self.conn.execute("""
            SELECT * FROM valuations 
            ORDER BY valuation_date DESC 
            LIMIT 1
        """).fetchall()
        
        if not result:
            return None
        
        row = result[0]
        return {
            'valuation_date': row[0],
            'current_price': row[1],
            'wacc': row[2],
            'fcf_year1': row[3],
            'fcf_year2': row[4],
            'fcf_year3': row[5],
            'fcf_year4': row[6],
            'fcf_year5': row[7],
            'terminal_value': row[8],
            'intrinsic_value_per_share': row[9],
            'margin_of_safety': row[10],
            'recommendation': row[11],
            'wacc_breakdown': json.loads(row[12]) if row[12] else {},
            'dcf_breakdown': json.loads(row[13]) if row[13] else {}
        }
    
    def get_current_price(self) -> Optional[float]:
        """Get latest price from market data."""
        result = self.conn.execute("""
            SELECT close FROM market_data 
            ORDER BY timestamp DESC 
            LIMIT 1
        """).fetchall()
        
        return result[0][0] if result else None
    
    def close(self):
        """Close database connection."""
        self.conn.close()
