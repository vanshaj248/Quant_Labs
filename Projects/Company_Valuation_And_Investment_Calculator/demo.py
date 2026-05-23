#!/usr/bin/env python3
"""
DCF Valuation Demo
Shows all features of the system with sample data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.valuation.tvm import TVMCalculator
from src.valuation.wacc import WACCCalculator
from src.valuation.dcf import DCFCalculator
from src.database.init_db import CompanyDatabase


def demo_tvm():
    """Demonstrate TVM calculations."""
    print("\n" + "="*70)
    print("  TIME VALUE OF MONEY (TVM) CALCULATOR")
    print("="*70)
    
    # PV of single cash flow
    pv = TVMCalculator.pv_single(fv=1000, rate=0.10, periods=5)
    print(f"\n1. Present Value of $1000 in 5 years @ 10%: ${pv:.2f}")
    
    # FV of single cash flow
    fv = TVMCalculator.fv_single(pv=1000, rate=0.10, periods=5)
    print(f"2. Future Value of $1000 in 5 years @ 10%: ${fv:.2f}")
    
    # Discount a series
    cash_flows = [100, 200, 300, 400, 500]  # millions
    discounted, total_pv = TVMCalculator.discount_cash_flows(cash_flows, 0.10)
    print(f"\n3. Discount Series of Cash Flows @ 10%:")
    for i, (cf, dcf) in enumerate(zip(cash_flows, discounted), 1):
        print(f"   Year {i}: ${cf}M → PV ${dcf:.2f}M")
    print(f"   Total PV: ${total_pv:.2f}M")
    
    # Terminal Value
    fcf_year5 = 500
    tv = TVMCalculator.terminal_value_perpetuity(fcf_year5, wacc=0.09, growth_rate=0.025)
    print(f"\n4. Terminal Value: FCF₅ × (1+g)/(WACC-g) = ${tv:.2f}M")
    
    # IRR
    cash_flows_irr = [-1000, 300, 300, 300, 300, 300]
    irr = TVMCalculator.irr(cash_flows_irr)
    print(f"\n5. IRR of project: {irr*100:.2f}%")


def demo_wacc():
    """Demonstrate WACC calculation."""
    print("\n" + "="*70)
    print("  WEIGHTED AVERAGE COST OF CAPITAL (WACC)")
    print("="*70)
    
    # Apple-like financials
    market_cap = 2850000    # $2.85T
    total_debt = 106589     # $106.6B
    interest_exp = 2931     # $2.931B
    beta = 1.24
    
    wacc_result = WACCCalculator.estimate_wacc(
        market_cap=market_cap,
        total_debt=total_debt,
        interest_expense=interest_exp,
        beta=beta,
        tax_rate=0.25
    )
    
    print(f"\nCompany: Apple Inc (AAPL)")
    print(f"  Market Cap: ${market_cap:,.0f}M")
    print(f"  Total Debt: ${total_debt:,.0f}M")
    print(f"  Beta: {wacc_result.beta}")
    print(f"\nRisk Assumptions:")
    print(f"  Risk-free Rate: {wacc_result.risk_free_rate*100:.2f}%")
    print(f"  Market Risk Premium: {wacc_result.market_risk_premium*100:.2f}%")
    print(f"\nCALC Results:")
    print(f"  Cost of Equity (CAPM): {wacc_result.cost_of_equity*100:.2f}%")
    print(f"  Cost of Debt (after-tax): {wacc_result.cost_of_debt*100:.2f}%")
    print(f"  Tax Rate: {wacc_result.tax_rate*100:.2f}%")
    print(f"\n>>> WACC: {wacc_result.wacc*100:.2f}%")
    
    return wacc_result


def demo_dcf(wacc_data):
    """Demonstrate DCF valuation."""
    print("\n" + "="*70)
    print("  DCF VALUATION MODEL")
    print("="*70)
    
    # 5-year FCF projections for Apple
    fcf_projections = [120000, 134400, 147840, 159667, 167650]  # millions
    current_price = 182.52
    shares = 15552  # millions
    net_debt = 78000  # millions
    
    valuation = DCFCalculator.calculate_dcf(
        ticker="AAPL",
        company_name="Apple Inc",
        current_price=current_price,
        fcf_projections=fcf_projections,
        wacc=wacc_data.wacc,
        terminal_growth_rate=0.025,
        shares_outstanding=shares,
        net_debt=net_debt
    )
    
    print(f"\nFree Cash Flow Projections:")
    for i, fcf in enumerate(fcf_projections, 1):
        print(f"  Year {i}: ${fcf:,.0f}M")
    
    print(f"\nDCF Calculation:")
    print(f"  Terminal Value: ${valuation.terminal_value:,.0f}M")
    print(f"  PV of FCFs (Yrs 1-5): ${valuation.pv_fcfs:,.0f}M")
    print(f"  PV of Terminal Value: ${valuation.pv_terminal_value:,.0f}M")
    print(f"  Enterprise Value: ${valuation.enterprise_value:,.0f}M")
    print(f"  Less: Net Debt: ${net_debt:,.0f}M")
    print(f"  Equity Value: ${valuation.equity_value:,.0f}M")
    
    print(f"\nValuation Results:")
    print(f"  Current Market Price: ${current_price:.2f}")
    print(f"  Intrinsic Value (DCF): ${valuation.intrinsic_value_per_share:.2f}")
    print(f"  Margin of Safety: {valuation.margin_of_safety*100:+.1f}%")
    print(f"  >>> Recommendation: {valuation.recommendation}")


def demo_database():
    """Demonstrate database operations."""
    print("\n" + "="*70)
    print("  DUCKDB OPERATIONS")
    print("="*70)
    
    db = CompanyDatabase()
    
    print(f"\nCompanies in Database:")
    companies = db.get_all_companies()
    for company in companies[:10]:
        print(f"  {company[0]}: {company[1]}")
    
    print(f"\nTotal companies: {len(companies)}")
    
    db.close()


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("  DCF VALUATION ANALYZER - FEATURE DEMO")
    print("="*70)
    
    # Demo TVM
    demo_tvm()
    
    # Demo WACC
    wacc_data = demo_wacc()
    
    # Demo DCF
    demo_dcf(wacc_data)
    
    # Demo Database
    demo_database()
    
    print("\n" + "="*70)
    print("  DEMO COMPLETE")
    print("="*70)
    print("\nNext Steps:")
    print("  1. Run: python main.py")
    print("     → Launches interactive TUI interface")
    print("\n  2. Run: python main.py --ingest AAPL MSFT")
    print("     → Fetches real data from Finnhub API")
    print("\n  3. Run: python main.py --valuate GOOGL")
    print("     → Performs DCF valuation on specific company")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
