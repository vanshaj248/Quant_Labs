# Company Valuation & Investment Calculator - Implementation Plan

## Project Status: Foundation Complete, Core Analysis Pending

### Phase 1: Financial Data Layer ✅ (In Progress)
**Goal:** Fetch and structure company financial data needed for valuation

- [ ] Create `src/financials/fetcher.py` - FMP API wrapper for:
  - Income statement (Revenue, EBIT, Net Income, Tax Rate)
  - Balance sheet (Total Debt, Equity, Interest Expense)
  - Cash flow statement (Free Cash Flow, CapEx)
  - Market cap, stock price, shares outstanding
  
- [ ] Create database schema for financial statements
- [ ] Test with chosen company (e.g., AAPL, INFOSYS)

### Phase 2: TVM & Valuation Calculators ✅ (Not Started)
**Goal:** Build core financial calculation functions

- [ ] Create `src/valuation/tvm.py`:
  - `present_value(fv, rate, periods)` - PV = FV / (1 + r)^n
  - `future_value(pv, rate, periods)` - FV = PV * (1 + r)^n
  - `npv(rate, cash_flows)` - Sum of discounted cash flows
  - `irr(cash_flows)` - IRR solver
  
- [ ] Create `src/valuation/wacc.py`:
  - Cost of equity (CAPM): Re = Rf + β(Rm - Rf)
  - Cost of debt: Rd = Interest Expense / Total Debt
  - WACC = (E/V) * Re + (D/V) * Rd * (1 - Tc)
  - Build-up: Calculate each component separately

- [ ] Create `src/valuation/dcf.py`:
  - Project 5-year FCFs (or use historical)
  - Calculate terminal value (Gordon Growth Model)
  - Discount all cash flows to PV using WACC
  - Calculate intrinsic value per share

### Phase 3: Analysis & Reporting ✅ (Not Started)
**Goal:** Generate valuation analysis and investment recommendation

- [ ] Create `src/analysis/valuation_report.py`:
  - Compare intrinsic value vs market price
  - Calculate upside/downside %
  - Dividend analysis and peer comparison
  - NPV/IRR analysis for hypothetical project

- [ ] Create `src/reports/investment_memo.py`:
  - Generate 1-page investment memo
  - Summary of key assumptions
  - Sensitivity analysis
  - Buy/Hold/Sell recommendation with reasoning

### Phase 4: Integration & Outputs ✅ (Not Started)
**Goal:** Complete end-to-end workflow

- [ ] Update `main.py` - Orchestrate full analysis
- [ ] Export results to:
  - Excel workbook with all calculations
  - Investment memo (PDF/Markdown)
  - Summary statistics

---

## Company Selection
**Suggested:** AAPL (Apple) or INFOSYS (if analyzing Indian market)
- Widely available data
- Clear financial statements
- Good for valuation practice

## Key Inputs Needed
- Risk-free rate (Rf) - Use 10Y Treasury yield
- Market risk premium (Rm - Rf) - ~6-7% historical average
- Company beta (β) - From FMP API
- Tax rate (Tc) - From income statement
- Terminal growth rate (g) - ~2-3% (GDP growth)

## Deliverables Checklist
- [ ] DCF model with WACC build-up
- [ ] NPV/IRR analysis of hypothetical project
- [ ] Intrinsic vs market price comparison
- [ ] Dividend policy summary
- [ ] 1-page investment memo (Buy/Hold/Sell)
- [ ] Python notebook or Excel workbook
