"""
Weighted Average Cost of Capital (WACC) Calculator
Calculates cost of equity (CAPM) and WACC
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class WACCComponents:
    """Store WACC components for transparency."""
    risk_free_rate: float
    market_risk_premium: float
    beta: float
    cost_of_equity: float
    cost_of_debt: float
    tax_rate: float
    debt_value: float
    equity_value: float
    wacc: float


class WACCCalculator:
    """Calculate WACC using CAPM and capital structure."""
    
    # Default assumptions
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5% (US 10-year Treasury)
    DEFAULT_MARKET_RISK_PREMIUM = 0.065  # 6.5% historical average
    DEFAULT_TAX_RATE = 0.25  # 25% corporate tax rate
    
    @staticmethod
    def capm_cost_of_equity(
        risk_free_rate: float,
        beta: float,
        market_risk_premium: float
    ) -> float:
        """
        Calculate cost of equity using CAPM.
        Re = Rf + β(Rm - Rf)
        """
        return risk_free_rate + beta * market_risk_premium
    
    @staticmethod
    def cost_of_debt_from_financials(
        total_debt: float,
        interest_expense: float,
        tax_rate: float
    ) -> float:
        """
        Calculate after-tax cost of debt.
        Rd = (Interest Expense / Total Debt) * (1 - Tax Rate)
        """
        if total_debt <= 0:
            return 0
        pre_tax_cost = interest_expense / total_debt
        return pre_tax_cost * (1 - tax_rate)
    
    @staticmethod
    def calculate_wacc(
        cost_of_equity: float,
        cost_of_debt: float,
        equity_value: float,
        debt_value: float,
        tax_rate: float = DEFAULT_TAX_RATE
    ) -> float:
        """
        Calculate WACC.
        WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
        where E = market value of equity, D = market value of debt, V = E + D
        """
        total_value = equity_value + debt_value
        if total_value <= 0:
            return cost_of_equity
        
        weight_equity = equity_value / total_value
        weight_debt = debt_value / total_value
        
        wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt * (1 - tax_rate))
        return wacc
    
    @staticmethod
    def estimate_wacc(
        market_cap: float,
        total_debt: float,
        interest_expense: float,
        beta: float,
        tax_rate: float = DEFAULT_TAX_RATE,
        risk_free_rate: float = DEFAULT_RISK_FREE_RATE,
        market_risk_premium: float = DEFAULT_MARKET_RISK_PREMIUM
    ) -> WACCComponents:
        """
        Estimate WACC from company financials.
        
        Args:
            market_cap: Market value of equity (in millions)
            total_debt: Total debt (in millions)
            interest_expense: Annual interest expense (in millions)
            beta: Stock beta
            tax_rate: Corporate tax rate (default 25%)
            risk_free_rate: Risk-free rate (default 4.5%)
            market_risk_premium: Market risk premium (default 6.5%)
        
        Returns:
            WACCComponents with all breakdown details
        """
        # Calculate cost of equity
        cost_of_equity = WACCCalculator.capm_cost_of_equity(
            risk_free_rate, beta, market_risk_premium
        )
        
        # Calculate cost of debt
        cost_of_debt = WACCCalculator.cost_of_debt_from_financials(
            total_debt, interest_expense, tax_rate
        )
        
        # Calculate WACC
        wacc = WACCCalculator.calculate_wacc(
            cost_of_equity, cost_of_debt, market_cap, total_debt, tax_rate
        )
        
        return WACCComponents(
            risk_free_rate=risk_free_rate,
            market_risk_premium=market_risk_premium,
            beta=beta,
            cost_of_equity=cost_of_equity,
            cost_of_debt=cost_of_debt,
            tax_rate=tax_rate,
            debt_value=total_debt,
            equity_value=market_cap,
            wacc=wacc
        )
