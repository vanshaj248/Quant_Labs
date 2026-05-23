"""
Comprehensive Valuation Engine
Brings together all components: Finnhub data, WACC, DCF calculations, and analysis
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "test"))

try:
    import finnhub
    from finnhub_pipeline import get_quote, get_key_metrics
except ImportError:
    finnhub = None

from src.database.init_db import CompanyDatabase
from src.valuation.dcf import DCFCalculator, DCFValuation
from src.valuation.wacc import WACCCalculator, WACCComponents
from src.valuation.tvm import TVMCalculator
from src.ingestion.ingestion import load_api_key_from_env


class CompanyValuationEngine:
    """Complete valuation engine for DCF analysis."""
    
    def __init__(self, api_key: str = None):
        """Initialize valuation engine."""
        self.api_key = api_key or load_api_key_from_env()
        self.client = finnhub.Client(api_key=self.api_key) if finnhub else None
        self.db = CompanyDatabase()
    
    def get_company_metrics(self, ticker: str) -> Dict:
        """Fetch company metrics from Finnhub."""
        try:
            if not self.client:
                return {}
            
            # Get metrics
            metrics = self.client.company_basic_financials(
                symbol=ticker.upper(), 
                metric="all"
            )
            
            return metrics.get("metric", {})
        except Exception as e:
            print(f"Error fetching metrics: {e}")
            return {}
    
    def estimate_fcf(self, ticker: str, years: int = 5) -> Tuple[float, list]:
        """
        Estimate 5-year FCF projections.
        Returns: (base_fcf, [fcf_year1, ..., fcf_year5])
        """
        try:
            # Get latest financials from Finnhub
            data = self.client.financials_reported(symbol=ticker.upper())
            
            if not data or "data" not in data:
                return 0, []
            
            reports = data.get("data", [])
            if not reports:
                return 0, []
            
            # Extract FCF from most recent report
            latest = reports[0]
            fcf = float(latest.get("fcf", 0))
            
            # Project FCF with declining growth rates
            growth_rates = [0.15, 0.12, 0.10, 0.08, 0.05]  # Declining growth
            projections = TVMCalculator.discount_cash_flows(
                [fcf * (1 + rate) for rate in growth_rates],
                0  # Use rate=0 just to multiply
            )
            
            # Recalculate with proper growth
            fcf_projections = []
            current_fcf = fcf
            for rate in growth_rates:
                current_fcf *= (1 + rate)
                fcf_projections.append(current_fcf)
            
            return fcf, fcf_projections
        
        except Exception as e:
            print(f"Error estimating FCF: {e}")
            return 0, []
    
    def run_valuation(self, ticker: str) -> Optional[DCFValuation]:
        """
        Run complete DCF valuation for a company.
        """
        ticker = ticker.upper()
        print(f"\n{'='*70}")
        print(f"  DCF VALUATION ANALYSIS - {ticker}")
        print(f"{'='*70}\n")
        
        try:
            # Get current price
            print("📊 Fetching market data...")
            metrics = self.get_company_metrics(ticker)
            
            if not metrics:
                print("❌ Unable to fetch company data")
                return None
            
            current_price = float(metrics.get("current_price", 100))
            market_cap = float(metrics.get("marketCap", 1000)) / 1_000_000  # Convert to millions
            beta = float(metrics.get("beta", 1.0))
            shares = float(metrics.get("shares", 1))
            
            print(f"  ✓ Current Price: ${current_price:.2f}")
            print(f"  ✓ Market Cap: ${market_cap:.0f}M")
            print(f"  ✓ Beta: {beta:.2f}")
            
            # Estimate WACC
            print(f"\n💰 Calculating WACC...")
            total_debt = float(metrics.get("totalDebt", 0)) / 1_000_000
            interest_exp = float(metrics.get("interestExpense", 0)) / 1_000_000
            
            wacc_components = WACCCalculator.estimate_wacc(
                market_cap=market_cap,
                total_debt=total_debt,
                interest_expense=interest_exp,
                beta=beta,
                tax_rate=0.25
            )
            
            print(f"  ✓ Cost of Equity (CAPM): {wacc_components.cost_of_equity*100:.2f}%")
            print(f"  ✓ Cost of Debt: {wacc_components.cost_of_debt*100:.2f}%")
            print(f"  ✓ WACC: {wacc_components.wacc*100:.2f}%")
            
            # Project FCF
            print(f"\n📈 Projecting Free Cash Flows...")
            base_fcf, fcf_projections = self.estimate_fcf(ticker)
            
            if not fcf_projections:
                print("  ⚠️ No FCF data available, using estimated growth")
                fcf_projections = [100 * (1.1 ** i) for i in range(1, 6)]  # Simple estimate
            
            print(f"  ✓ 5-Year Projections:")
            for i, fcf in enumerate(fcf_projections, 1):
                print(f"    Year {i}: ${fcf:.0f}M")
            
            # Run DCF
            print(f"\n🎯 Running DCF Valuation...")
            net_debt = total_debt - float(metrics.get("cash", 0)) / 1_000_000
            
            valuation = DCFCalculator.calculate_dcf(
                ticker=ticker,
                company_name=ticker,
                current_price=current_price,
                fcf_projections=fcf_projections,
                wacc=wacc_components.wacc,
                terminal_growth_rate=0.025,
                shares_outstanding=shares,
                net_debt=max(0, net_debt)
            )
            
            # Store in database
            self.db.add_valuation(ticker, {
                'valuation_date': datetime.now().date(),
                'current_price': current_price,
                'wacc': wacc_components.wacc,
                'intrinsic_value_per_share': valuation.intrinsic_value_per_share,
                'margin_of_safety': valuation.margin_of_safety,
                'recommendation': valuation.recommendation,
                'dcf_full_data': {
                    'fcf_projections': fcf_projections,
                    'terminal_value': valuation.terminal_value,
                    'pv_terminal': valuation.pv_terminal_value,
                }
            })
            
            return valuation
        
        except Exception as e:
            print(f"❌ Error running valuation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def print_valuation_report(self, valuation: DCFValuation):
        """Print detailed valuation report."""
        print(f"\n{'='*70}")
        print(f"  VALUATION RESULTS")
        print(f"{'='*70}\n")
        
        print(f"Ticker: {valuation.ticker}")
        print(f"Current Market Price: ${valuation.current_price:.2f}")
        print(f"Intrinsic Value (DCF): ${valuation.intrinsic_value_per_share:.2f}")
        print(f"Margin of Safety: {valuation.margin_of_safety*100:+.1f}%")
        print(f"\nRecommendation: {valuation.recommendation}")
        
        upside, direction = valuation.upside_downside()
        print(f"{direction}: {upside:+.1f}%")
        
        print(f"\n{'='*70}")
        print(f"DCF Components:")
        print(f"  PV of FCFs (Years 1-5): ${valuation.pv_fcfs:.0f}M")
        print(f"  Terminal Value: ${valuation.terminal_value:.0f}M")
        print(f"  PV of Terminal Value: ${valuation.pv_terminal_value:.0f}M")
        print(f"  Enterprise Value: ${valuation.enterprise_value:.0f}M")
        print(f"  Equity Value: ${valuation.equity_value:.0f}M")
        print(f"{'='*70}\n")
    
    def close(self):
        """Close database connection."""
        self.db.close()


def run_valuation(ticker: str, api_key: str = None):
    """Run valuation and print report."""
    engine = CompanyValuationEngine(api_key)
    
    valuation = engine.run_valuation(ticker)
    
    if valuation:
        engine.print_valuation_report(valuation)
    
    engine.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        run_valuation(ticker)
    else:
        print("Usage: python valuation_engine.py TICKER")
