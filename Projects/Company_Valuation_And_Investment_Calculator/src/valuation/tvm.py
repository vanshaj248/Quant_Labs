"""
Time Value of Money (TVM) Calculator
Handles PV, FV, and discount calculations
"""

import numpy as np
from typing import List, Dict, Tuple


class TVMCalculator:
    """Calculate present/future values with various discount rates."""
    
    @staticmethod
    def pv_single(fv: float, rate: float, periods: int) -> float:
        """Calculate present value of a single future cash flow."""
        if rate >= 1:
            return 0
        return fv / ((1 + rate) ** periods)
    
    @staticmethod
    def fv_single(pv: float, rate: float, periods: int) -> float:
        """Calculate future value of a single present cash flow."""
        return pv * ((1 + rate) ** periods)
    
    @staticmethod
    def pv_annuity(pmt: float, rate: float, periods: int) -> float:
        """Calculate present value of an annuity (equal payments)."""
        if rate == 0:
            return pmt * periods
        return pmt * (1 - (1 + rate) ** (-periods)) / rate
    
    @staticmethod
    def discount_cash_flows(cash_flows: List[float], discount_rate: float) -> Tuple[List[float], float]:
        """
        Discount a series of cash flows.
        Returns: (discounted_cfs, total_pv)
        """
        discounted = []
        total_pv = 0
        
        for t, cf in enumerate(cash_flows, 1):
            pv = TVMCalculator.pv_single(cf, discount_rate, t)
            discounted.append(pv)
            total_pv += pv
        
        return discounted, total_pv
    
    @staticmethod
    def terminal_value_perpetuity(fcf: float, wacc: float, growth_rate: float) -> float:
        """
        Calculate terminal value using perpetuity with growth.
        TV = FCF * (1 + g) / (WACC - g)
        """
        if wacc <= growth_rate:
            return 0
        return fcf * (1 + growth_rate) / (wacc - growth_rate)
    
    @staticmethod
    def irr(cash_flows: List[float], guess: float = 0.1) -> float:
        """Calculate IRR using Newton-Raphson method."""
        def npv(rate, cfs):
            return sum(cf / (1 + rate) ** t for t, cf in enumerate(cfs))
        
        def npv_derivative(rate, cfs):
            return sum(-t * cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cfs))
        
        rate = guess
        for _ in range(100):
            npv_val = npv(rate, cash_flows)
            if abs(npv_val) < 1e-6:
                return rate
            npv_der = npv_derivative(rate, cash_flows)
            if npv_der == 0:
                break
            rate = rate - npv_val / npv_der
        
        return rate
    
    @staticmethod
    def npv(cash_flows: List[float], discount_rate: float) -> float:
        """Calculate Net Present Value."""
        _, total_pv = TVMCalculator.discount_cash_flows(cash_flows, discount_rate)
        return total_pv
