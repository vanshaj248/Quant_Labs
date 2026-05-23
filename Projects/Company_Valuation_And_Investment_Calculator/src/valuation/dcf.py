"""
Discounted Cash Flow (DCF) Valuation Model
Projects FCFs, discounts them, and calculates intrinsic value
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from src.valuation.tvm import TVMCalculator
from src.valuation.wacc import WACCComponents


@dataclass
class DCFValuation:
    """Store DCF valuation results."""
    ticker: str
    company_name: str
    current_price: float
    
    # Projection period
    fcf_projections: List[float]  # 5-year FCFs
    wacc: float
    terminal_growth_rate: float
    
    # Calculations
    discounted_fcfs: List[float]
    pv_fcfs: float
    terminal_value: float
    pv_terminal_value: float
    enterprise_value: float
    
    # Per share metrics
    shares_outstanding: float
    net_debt: float
    equity_value: float
    intrinsic_value_per_share: float
    
    # Valuation decision
    margin_of_safety: float  # %
    recommendation: str  # Buy, Hold, Sell
    
    def upside_downside(self) -> Tuple[float, str]:
        """Calculate upside/downside from current price."""
        diff = self.intrinsic_value_per_share - self.current_price
        pct = (diff / self.current_price) * 100 if self.current_price > 0 else 0
        direction = "Upside" if pct > 0 else "Downside"
        return pct, direction


class DCFCalculator:
    """Perform DCF valuation analysis."""
    
    @staticmethod
    def project_fcf_simple(
        base_fcf: float,
        growth_rates: List[float]
    ) -> List[float]:
        """
        Project FCF using growth rates.
        
        Args:
            base_fcf: FCF in year 0
            growth_rates: Growth rates for years 1-5
        """
        projections = [base_fcf]
        for rate in growth_rates:
            next_fcf = projections[-1] * (1 + rate)
            projections.append(next_fcf)
        return projections[1:]  # Return years 1-5
    
    @staticmethod
    def calculate_dcf(
        ticker: str,
        company_name: str,
        current_price: float,
        fcf_projections: List[float],
        wacc: float,
        terminal_growth_rate: float = 0.025,
        shares_outstanding: float = 1.0,
        net_debt: float = 0,
    ) -> DCFValuation:
        """
        Calculate DCF valuation.
        
        Args:
            ticker: Stock ticker
            company_name: Company name
            current_price: Current market price per share
            fcf_projections: 5-year projected FCFs (in millions)
            wacc: Weighted average cost of capital
            terminal_growth_rate: Perpetual growth rate (default 2.5%)
            shares_outstanding: Shares outstanding (in millions)
            net_debt: Net debt = Total Debt - Cash (in millions)
        
        Returns:
            DCFValuation object with full analysis
        """
        # Discount FCFs
        discounted_fcfs, pv_fcfs = TVMCalculator.discount_cash_flows(
            fcf_projections, wacc
        )
        
        # Calculate terminal value
        year5_fcf = fcf_projections[-1]
        terminal_value = TVMCalculator.terminal_value_perpetuity(
            year5_fcf, wacc, terminal_growth_rate
        )
        pv_terminal = TVMCalculator.pv_single(terminal_value, wacc, len(fcf_projections))
        
        # Enterprise value
        enterprise_value = pv_fcfs + pv_terminal
        
        # Equity value
        equity_value = enterprise_value - net_debt
        
        # Intrinsic value per share
        intrinsic_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
        
        # Valuation decision
        margin_of_safety = (intrinsic_value_per_share - current_price) / current_price if current_price > 0 else 0
        
        if margin_of_safety > 0.20:  # > 20% upside
            recommendation = "STRONG BUY"
        elif margin_of_safety > 0.10:  # > 10% upside
            recommendation = "BUY"
        elif margin_of_safety > -0.10:  # Within 10% margin
            recommendation = "HOLD"
        elif margin_of_safety > -0.20:  # Within 20% downside
            recommendation = "SELL"
        else:
            recommendation = "STRONG SELL"
        
        return DCFValuation(
            ticker=ticker,
            company_name=company_name,
            current_price=current_price,
            fcf_projections=fcf_projections,
            wacc=wacc,
            terminal_growth_rate=terminal_growth_rate,
            discounted_fcfs=discounted_fcfs,
            pv_fcfs=pv_fcfs,
            terminal_value=terminal_value,
            pv_terminal_value=pv_terminal,
            enterprise_value=enterprise_value,
            shares_outstanding=shares_outstanding,
            net_debt=net_debt,
            equity_value=equity_value,
            intrinsic_value_per_share=intrinsic_value_per_share,
            margin_of_safety=margin_of_safety,
            recommendation=recommendation
        )
    
    @staticmethod
    def sensitivity_analysis(
        base_valuation: DCFValuation,
        wacc_range: Tuple[float, float],
        growth_range: Tuple[float, float],
        steps: int = 5
    ) -> Dict[float, Dict[float, float]]:
        """
        Perform sensitivity analysis on WACC and terminal growth rate.
        
        Returns:
            Dict of {wacc: {growth: intrinsic_value}}
        """
        import numpy as np
        
        wacc_values = np.linspace(wacc_range[0], wacc_range[1], steps)
        growth_values = np.linspace(growth_range[0], growth_range[1], steps)
        
        results = {}
        
        for wacc in wacc_values:
            results[wacc] = {}
            for growth in growth_values:
                valuation = DCFCalculator.calculate_dcf(
                    base_valuation.ticker,
                    base_valuation.company_name,
                    base_valuation.current_price,
                    base_valuation.fcf_projections,
                    wacc,
                    growth,
                    base_valuation.shares_outstanding,
                    base_valuation.net_debt
                )
                results[wacc][growth] = valuation.intrinsic_value_per_share
        
        return results
