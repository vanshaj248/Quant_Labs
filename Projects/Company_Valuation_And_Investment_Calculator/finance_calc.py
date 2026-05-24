"""
Financial Calculations: TVM, WACC, DCF, NPV, IRR — all manual formulas.
"""
import math
from typing import Optional


# ── Time Value of Money ────────────────────────────────────────────────────────

def present_value(fv: float, rate: float, n: int) -> float:
    """PV = FV / (1 + r)^n"""
    if rate <= -1:
        return 0.0
    return fv / ((1 + rate) ** n)


def future_value(pv: float, rate: float, n: int) -> float:
    """FV = PV * (1 + r)^n"""
    return pv * ((1 + rate) ** n)


def pv_annuity(pmt: float, rate: float, n: int) -> float:
    """PV of ordinary annuity."""
    if rate == 0:
        return pmt * n
    return pmt * (1 - (1 + rate) ** (-n)) / rate


def fv_annuity(pmt: float, rate: float, n: int) -> float:
    """FV of ordinary annuity."""
    if rate == 0:
        return pmt * n
    return pmt * ((1 + rate) ** n - 1) / rate


# ── CAPM ──────────────────────────────────────────────────────────────────────

def capm_cost_of_equity(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float = 0.055,
) -> float:
    """Ke = Rf + β × (Rm - Rf)"""
    return risk_free_rate + beta * market_risk_premium


# ── WACC ──────────────────────────────────────────────────────────────────────

def compute_wacc(
    cost_of_equity: float,
    cost_of_debt: float,
    equity_value: float,
    debt_value: float,
    tax_rate: float = 0.25,
) -> dict:
    """
    WACC = (E/V)*Ke + (D/V)*Kd*(1-t)
    Returns dict with wacc and component weights.
    """
    total = equity_value + debt_value
    if total == 0:
        return {"wacc": 0.10, "we": 1.0, "wd": 0.0, "ke": cost_of_equity, "kd": cost_of_debt}
    we = equity_value / total
    wd = debt_value / total
    wacc = we * cost_of_equity + wd * cost_of_debt * (1 - tax_rate)
    return {
        "wacc":           wacc,
        "we":             we,
        "wd":             wd,
        "ke":             cost_of_equity,
        "kd_after_tax":   cost_of_debt * (1 - tax_rate),
        "equity_value":   equity_value,
        "debt_value":     debt_value,
        "tax_rate":       tax_rate,
    }


# ── Free Cash Flow Projection ──────────────────────────────────────────────────

def project_fcfs(
    base_fcf: float,
    growth_rates: list[float],   # one per year
) -> list[float]:
    """Project FCFs for each year using given growth rates."""
    fcfs = []
    current = base_fcf
    for g in growth_rates:
        current = current * (1 + g)
        fcfs.append(current)
    return fcfs


# ── Terminal Value ─────────────────────────────────────────────────────────────

def terminal_value_gordon(
    terminal_fcf: float,
    wacc: float,
    terminal_growth: float = 0.025,
) -> float:
    """TV = FCF_n * (1+g) / (WACC - g)"""
    if wacc <= terminal_growth:
        return 0.0
    return terminal_fcf * (1 + terminal_growth) / (wacc - terminal_growth)


# ── DCF Valuation ─────────────────────────────────────────────────────────────

def dcf_valuation(
    base_fcf: float,
    wacc: float,
    growth_rates: list[float],
    terminal_growth: float = 0.025,
    net_debt: float = 0.0,
    shares_outstanding: float = 1.0,
    cash: float = 0.0,
) -> dict:
    """
    Full DCF:
      1. Project FCFs
      2. Discount each FCF at WACC
      3. Terminal value discounted back
      4. Enterprise value = sum PV(FCFs) + PV(TV)
      5. Equity value = EV - Net Debt
      6. Intrinsic value per share
    """
    projected = project_fcfs(base_fcf, growth_rates)
    n = len(projected)

    pv_fcfs = []
    for i, fcf in enumerate(projected):
        pv = present_value(fcf, wacc, i + 1)
        pv_fcfs.append({"year": i + 1, "fcf": fcf, "pv": pv})

    tv = terminal_value_gordon(projected[-1], wacc, terminal_growth)
    pv_tv = present_value(tv, wacc, n)

    sum_pv_fcfs = sum(x["pv"] for x in pv_fcfs)
    enterprise_value = sum_pv_fcfs + pv_tv
    equity_value = enterprise_value - net_debt + cash
    intrinsic_per_share = equity_value / max(shares_outstanding, 1)

    return {
        "projected_fcfs":      pv_fcfs,
        "terminal_value":      tv,
        "pv_terminal_value":   pv_tv,
        "sum_pv_fcfs":         sum_pv_fcfs,
        "enterprise_value":    enterprise_value,
        "equity_value":        equity_value,
        "intrinsic_per_share": intrinsic_per_share,
        "shares":              shares_outstanding,
        "net_debt":            net_debt,
    }


# ── NPV ───────────────────────────────────────────────────────────────────────

def compute_npv(
    initial_investment: float,
    cash_flows: list[float],
    rate: float,
) -> float:
    """NPV = -C0 + Σ CF_t / (1+r)^t"""
    npv = -initial_investment
    for t, cf in enumerate(cash_flows, start=1):
        npv += cf / ((1 + rate) ** t)
    return npv


# ── IRR ───────────────────────────────────────────────────────────────────────

def compute_irr(
    initial_investment: float,
    cash_flows: list[float],
    guess: float = 0.10,
    max_iter: int = 1000,
    tol: float = 1e-7,
) -> Optional[float]:
    """
    Find IRR via Newton-Raphson bisection.
    IRR is the rate that makes NPV = 0.
    """
    all_flows = [-initial_investment] + list(cash_flows)

    def npv_fn(r):
        return sum(cf / ((1 + r) ** t) for t, cf in enumerate(all_flows))

    def npv_deriv(r):
        return sum(-t * cf / ((1 + r) ** (t + 1)) for t, cf in enumerate(all_flows) if t > 0)

    # Try bracketing
    lo, hi = -0.999, 10.0
    if npv_fn(lo) * npv_fn(hi) > 0:
        # Scan for sign change
        for test in [x / 100 for x in range(-99, 1000)]:
            if npv_fn(lo) * npv_fn(test) <= 0:
                hi = test
                break
        else:
            return None

    # Bisection
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        val = npv_fn(mid)
        if abs(val) < tol:
            return mid
        if npv_fn(lo) * val < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


# ── Sensitivity Analysis ───────────────────────────────────────────────────────

def wacc_sensitivity(
    base_fcf: float,
    growth_rates: list[float],
    terminal_growth: float,
    net_debt: float,
    shares: float,
    cash: float,
    wacc_range: list[float] = None,
) -> list[dict]:
    """Return intrinsic values across a range of WACCs."""
    if wacc_range is None:
        wacc_range = [w / 100 for w in range(6, 17)]
    results = []
    for w in wacc_range:
        val = dcf_valuation(base_fcf, w, growth_rates, terminal_growth,
                            net_debt, shares, cash)
        results.append({"wacc": w, "intrinsic": val["intrinsic_per_share"]})
    return results


# ── Helper: derive financials from Finnhub metrics ────────────────────────────

def derive_financials_from_metrics(metrics: dict, profile: dict) -> dict:
    """
    Build a structured financials dict from Finnhub's metric blob.
    Returns best-estimate values for WACC/DCF inputs.
    """
    m = metrics.get("metric", metrics)  # sometimes nested

    # Shares (in millions from finnhub)
    shares_millions = (
        m.get("sharesOutstanding")
        or profile.get("shareOutstanding", 0)
    )
    shares = (shares_millions or 0) * 1e6

    market_cap = (profile.get("marketCapitalization", 0) or 0) * 1e6

    # Price
    price = market_cap / max(shares, 1)

    # Beta
    beta = m.get("beta") or 1.0

    # Revenue, net income (TTM)
    revenue_ttm    = m.get("revenueTTM") or m.get("revenuePerShareTTM", 0) * shares / 1e6
    net_income_ttm = m.get("netIncomeTTM") or 0

    # FCF
    fcf_per_share = m.get("freeCashFlowTTM") or m.get("freeCashFlowPerShareTTM") or 0
    if fcf_per_share and shares > 0:
        fcf_ttm = fcf_per_share * (shares if fcf_per_share < 1000 else 1)
    else:
        # Fallback: use EBITDA margin
        ebitda_margin = m.get("ebitdaMarginTTM") or 0.15
        fcf_ttm = revenue_ttm * ebitda_margin * 0.6 if revenue_ttm else 0

    # Ensure FCF is reasonable (in actual dollars not per-share)
    # If FCF looks like per-share value, multiply by shares
    if 0 < abs(fcf_ttm) < 1000 and shares > 1e6:
        fcf_ttm = fcf_ttm * shares

    # Debt
    total_debt = m.get("totalDebt") or m.get("longTermDebt") or 0
    if total_debt and total_debt < 1e6 and shares > 1e6:
        total_debt = total_debt * 1e6  # convert millions

    # Equity (market cap proxy)
    total_equity = market_cap if market_cap > 0 else (shares * price)

    # Interest expense → cost of debt
    interest_exp = m.get("interestExpenseAnnual") or m.get("interestExpense") or 0
    if total_debt > 0 and interest_exp > 0:
        cost_of_debt = interest_exp / total_debt
    else:
        cost_of_debt = 0.04  # default 4%

    # Cap cost of debt sanely
    cost_of_debt = min(max(cost_of_debt, 0.01), 0.15)

    # Cash
    cash = m.get("cashAndEquivalentsAnnual") or m.get("cashAndCashEquivalents") or 0
    if cash and cash < 1e6 and shares > 1e6:
        cash = cash * 1e6

    # Dividend
    div_yield = m.get("dividendYieldIndicatedAnnual") or m.get("dividendYield") or 0

    # EPS
    eps_ttm = m.get("epsTTM") or m.get("epsBasicExclExtraItemsTTM") or 0

    # P/E
    pe_ratio = m.get("peBasicExclExtraTTM") or m.get("peRatio") or 0

    # Revenue growth (5yr CAGR)
    rev_growth_5y = m.get("revenueGrowth5Y") or m.get("revenueGrowthRate5Y") or 0.08

    return {
        "shares":         shares,
        "market_cap":     market_cap,
        "price":          price,
        "beta":           beta,
        "revenue_ttm":    revenue_ttm,
        "net_income_ttm": net_income_ttm,
        "fcf_ttm":        fcf_ttm,
        "total_debt":     total_debt,
        "total_equity":   total_equity,
        "interest_exp":   interest_exp,
        "cost_of_debt":   cost_of_debt,
        "cash":           cash,
        "net_debt":       max(total_debt - cash, 0),
        "div_yield":      div_yield,
        "eps_ttm":        eps_ttm,
        "pe_ratio":       pe_ratio,
        "rev_growth_5y":  rev_growth_5y,
    }


def run_full_valuation(
    fin: dict,
    market_price: float,
    risk_free_rate: float = 0.045,
    market_risk_premium: float = 0.055,
    terminal_growth: float = 0.025,
    project_years: int = 5,
    tax_rate: float = 0.25,
) -> dict:
    """
    One-shot full valuation pipeline.
    fin: dict from derive_financials_from_metrics()
    """
    # 1. Cost of equity (CAPM)
    beta = max(fin.get("beta", 1.0) or 1.0, 0.1)
    ke = capm_cost_of_equity(risk_free_rate, beta, market_risk_premium)

    # 2. WACC
    wacc_res = compute_wacc(
        ke,
        fin.get("cost_of_debt", 0.04),
        fin.get("total_equity", 0),
        fin.get("total_debt", 0),
        tax_rate,
    )
    wacc = wacc_res["wacc"]
    wacc = max(min(wacc, 0.25), 0.05)  # sanity clamp 5–25%

    # 3. FCF projection
    base_fcf = fin.get("fcf_ttm", 0)
    rev_growth = fin.get("rev_growth_5y", 0.08) or 0.08
    # Use declining growth schedule
    growth_rates = []
    g = min(max(rev_growth, 0.03), 0.30)
    for i in range(project_years):
        growth_rates.append(g * max(1 - i * 0.1, 0.5))

    # 4. DCF
    shares = fin.get("shares", 1)
    net_debt = fin.get("net_debt", 0)
    cash = fin.get("cash", 0)

    dcf = dcf_valuation(
        base_fcf, wacc, growth_rates, terminal_growth,
        net_debt, shares, cash,
    )

    # 5. Hypothetical project NPV/IRR
    # Assume a capex project = 10% of market cap, returns 12% of initial per yr for 7 yrs
    project_cost = fin.get("market_cap", 0) * 0.05
    if project_cost <= 0:
        project_cost = abs(base_fcf) * 2
    project_cfs = [project_cost * 0.15 * (1.05 ** y) for y in range(7)]
    npv_proj = compute_npv(project_cost, project_cfs, wacc)
    irr_proj = compute_irr(project_cost, project_cfs)

    # 6. TVM examples (5-year PV/FV of FCFs)
    tvm_table = []
    for item in dcf["projected_fcfs"]:
        yr = item["year"]
        pv = present_value(item["fcf"], wacc, yr)
        fv = future_value(item["fcf"], wacc, project_years - yr)
        tvm_table.append({
            "year": yr, "fcf": item["fcf"],
            "pv": pv, "fv": fv,
        })

    # 7. Margin of safety
    intrinsic = dcf["intrinsic_per_share"]
    if market_price > 0 and intrinsic > 0:
        upside_pct = (intrinsic - market_price) / market_price * 100
    else:
        upside_pct = 0.0

    valuation_label = (
        "🟢 UNDERVALUED" if upside_pct > 10
        else "🔴 OVERVALUED" if upside_pct < -10
        else "🟡 FAIRLY VALUED"
    )

    # Sensitivity
    sensitivity = wacc_sensitivity(
        base_fcf, growth_rates, terminal_growth,
        net_debt, shares, cash,
    )

    return {
        "wacc":             wacc,
        "ke":               ke,
        "beta":             beta,
        "wacc_details":     wacc_res,
        "growth_rates":     growth_rates,
        "dcf":              dcf,
        "intrinsic_value":  intrinsic,
        "market_price":     market_price,
        "upside_pct":       upside_pct,
        "valuation_label":  valuation_label,
        "npv_project":      npv_proj,
        "irr_project":      irr_proj or 0.0,
        "project_cost":     project_cost,
        "project_cfs":      project_cfs,
        "tvm_table":        tvm_table,
        "sensitivity":      sensitivity,
        "risk_free_rate":   risk_free_rate,
        "terminal_growth":  terminal_growth,
    }
