"""
DuckDB Database Schema and Initialization
Stores company financial data, valuations, and market metrics
"""

import duckdb
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List


class CompanyDatabase:
    """Manage DuckDB for company financial data."""
    
    def __init__(self, db_path: str = "data/company_valuations.duckdb"):
        """Initialize database connection."""
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(self.db_path)
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Create all tables if they don't exist."""
        
        # Financial data (annual)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS financials (
                ticker VARCHAR NOT NULL,
                fiscal_year INTEGER NOT NULL,
                revenue DOUBLE,
                gross_profit DOUBLE,
                operating_income DOUBLE,
                net_income DOUBLE,
                ebitda DOUBLE,
                free_cash_flow DOUBLE,
                operating_cash_flow DOUBLE,
                capital_expenditure DOUBLE,
                total_assets DOUBLE,
                total_liabilities DOUBLE,
                total_equity DOUBLE,
                cash_and_equivalents DOUBLE,
                total_debt DOUBLE,
                interest_expense DOUBLE,
                shares_outstanding DOUBLE,
                eps DOUBLE,
                book_value_per_share DOUBLE,
                last_updated TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (ticker, fiscal_year)
            )
        """)
        
        # Market data (daily)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                ticker VARCHAR NOT NULL,
                trade_date DATE NOT NULL,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume BIGINT,
                adjusted_close DOUBLE,
                last_updated TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (ticker, trade_date)
            )
        """)
        
        # Valuation metrics (calculated)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS valuations (
                ticker VARCHAR NOT NULL,
                valuation_date DATE NOT NULL,
                current_price DOUBLE,
                market_cap DOUBLE,
                beta DOUBLE,
                pe_ratio DOUBLE,
                pb_ratio DOUBLE,
                dividend_yield DOUBLE,
                roe DOUBLE,
                roa DOUBLE,
                current_ratio DOUBLE,
                debt_to_equity DOUBLE,
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
                dcf_data JSON,
                last_updated TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (ticker, valuation_date)
            )
        """)
        
        # Dividend data
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dividends (
                ticker VARCHAR NOT NULL,
                ex_date DATE NOT NULL,
                payment_date DATE,
                dividend_per_share DOUBLE,
                dividend_yield DOUBLE,
                last_updated TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (ticker, ex_date)
            )
        """)
        
        # Company profiles (insert first)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                ticker VARCHAR PRIMARY KEY,
                name VARCHAR NOT NULL,
                sector VARCHAR,
                industry VARCHAR,
                country VARCHAR,
                website VARCHAR,
                market_cap DOUBLE,
                employees INTEGER,
                founded_year INTEGER,
                description TEXT,
                last_updated TIMESTAMP DEFAULT current_timestamp
            )
        """)
    
    def add_company(self, ticker: str, name: str, sector: str = None, 
                   industry: str = None, country: str = None, website: str = None,
                   market_cap: float = None, employees: int = None,
                   founded_year: int = None, description: str = None):
        """Add or update company profile."""
        try:
            self.conn.execute("DELETE FROM companies WHERE ticker = ?", [ticker])
        except:
            pass
        
        self.conn.execute("""
            INSERT INTO companies (ticker, name, sector, industry, country, 
                                   website, market_cap, employees, founded_year, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [ticker, name, sector, industry, country, website, market_cap, 
              employees, founded_year, description])
    
    def add_financials(self, ticker: str, fiscal_year: int, data: Dict):
        """Add annual financial data."""
        try:
            self.conn.execute("DELETE FROM financials WHERE ticker = ? AND fiscal_year = ?",
                            [ticker, fiscal_year])
        except:
            pass
        
        self.conn.execute("""
            INSERT INTO financials (
                ticker, fiscal_year, revenue, gross_profit, operating_income, net_income,
                ebitda, free_cash_flow, operating_cash_flow, capital_expenditure,
                total_assets, total_liabilities, total_equity, cash_and_equivalents,
                total_debt, interest_expense, shares_outstanding, eps,
                book_value_per_share
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [ticker, fiscal_year, 
              data.get('revenue'), data.get('gross_profit'), data.get('operating_income'),
              data.get('net_income'), data.get('ebitda'), data.get('free_cash_flow'),
              data.get('operating_cash_flow'), data.get('capital_expenditure'),
              data.get('total_assets'), data.get('total_liabilities'), 
              data.get('total_equity'), data.get('cash_and_equivalents'),
              data.get('total_debt'), data.get('interest_expense'),
              data.get('shares_outstanding'), data.get('eps'),
              data.get('book_value_per_share')])
    
    def add_valuation(self, ticker: str, valuation_data: Dict):
        """Add valuation metrics."""
        val_date = valuation_data.get('valuation_date', datetime.now().date())
        try:
            self.conn.execute("DELETE FROM valuations WHERE ticker = ? AND valuation_date = ?",
                            [ticker, val_date])
        except:
            pass
        
        self.conn.execute("""
            INSERT INTO valuations (
                ticker, valuation_date, current_price, wacc,
                intrinsic_value_per_share, margin_of_safety,
                recommendation, dcf_data
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            ticker, 
            valuation_data.get('valuation_date', datetime.now().date()),
            valuation_data.get('current_price'),
            valuation_data.get('wacc'),
            valuation_data.get('intrinsic_value_per_share'),
            valuation_data.get('margin_of_safety'),
            valuation_data.get('recommendation'),
            json.dumps(valuation_data.get('dcf_full_data', {}))
        ])
    
    def get_company_financials(self, ticker: str, years: int = 5) -> List[Dict]:
        """Get recent financial data for a company."""
        result = self.conn.execute(f"""
            SELECT * FROM financials 
            WHERE ticker = ?
            ORDER BY fiscal_year DESC
            LIMIT {years}
        """, [ticker]).fetchall()
        return result
    
    def get_latest_valuation(self, ticker: str) -> Optional[Dict]:
        """Get most recent valuation for a company."""
        result = self.conn.execute("""
            SELECT * FROM valuations 
            WHERE ticker = ?
            ORDER BY valuation_date DESC
            LIMIT 1
        """, [ticker]).fetchone()
        return result
    
    def get_all_companies(self) -> List[Dict]:
        """Get all companies in database."""
        return self.conn.execute("SELECT * FROM companies ORDER BY ticker").fetchall()
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def init_default_companies():
    """Initialize database with Top 10 NASDAQ companies."""
    db = CompanyDatabase()
    
    nasdaq_top10 = [
        ("AAPL", "Apple Inc", "Technology", "Consumer Electronics"),
        ("MSFT", "Microsoft Corporation", "Technology", "Software"),
        ("GOOGL", "Alphabet Inc", "Technology", "Internet Services"),
        ("AMZN", "Amazon.com Inc", "Consumer", "Internet Retail"),
        ("NVDA", "NVIDIA Corporation", "Technology", "Semiconductors"),
        ("META", "Meta Platforms Inc", "Technology", "Internet Services"),
        ("TSLA", "Tesla Inc", "Automotive", "Electric Vehicles"),
        ("BRK.B", "Berkshire Hathaway", "Finance", "Diversified"),
        ("JPM", "JPMorgan Chase", "Finance", "Banking"),
        ("V", "Visa Inc", "Finance", "Payment Processing"),
    ]
    
    for ticker, name, sector, industry in nasdaq_top10:
        db.add_company(ticker, name, sector, industry, "USA")
    
    db.close()
    print("✓ Database initialized with Top 10 NASDAQ companies")
