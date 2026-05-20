# Project Architecture Overview

## Data Flow

```
External APIs
    ├── Alpaca API (Historical prices, market data)
    ├── FMP API (Financial statements, company data)
    └── Market indices (Risk-free rate, market returns)
              ↓
         [API Clients]
         src/api/client.py
              ↓
    [Data Ingestion Layer]
    src/ingestion/fetch_bars.py
              ↓
    [DuckDB Database]
    data/market_data.duckdb
              ↓
    [Analysis Layer]
    ├── TVM Calculator (src/valuation/tvm.py)
    ├── WACC Builder (src/valuation/wacc.py)
    ├── DCF Model (src/valuation/dcf.py)
    └── NPV/IRR Analysis
              ↓
    [Reporting]
    ├── Valuation Report
    ├── Investment Memo
    └── Excel Export
```

## M1 Concepts Applied

### 1. Time Value of Money (TVM)
- Discount 5-year FCFs using WACC
- Calculate terminal value using perpetuity growth
- Present value all cash flows

### 2. Capital Structure & WACC
- Estimate cost of equity (CAPM)
- Estimate cost of debt (from financials)
- Calculate WACC using D/E ratio

### 3. DCF Valuation
- Project historical or assumed FCFs for 5 years
- Terminal value = FCF₅ * (1 + g) / (WACC - g)
- Intrinsic Value = Σ[FCF / (1 + WACC)^t] + PV(Terminal Value)
- Price per share = Intrinsic Value / Shares Outstanding

### 4. NPV & IRR Analysis
- Evaluate hypothetical new project
- NPV = Σ[CF / (1 + WACC)^t] - Initial Investment
- Compare IRR vs WACC for project acceptance

### 5. Investment Decision
- Compare intrinsic vs market price
- Recommendation: Buy if undervalued, Sell if overvalued

---

## Next Steps

1. **Choose Company** - Pick AAPL or INFOSYS
2. **Build Financials Module** - Fetch & store financial data
3. **Build Calculators** - Implement TVM, WACC, DCF functions
4. **Run Analysis** - Generate valuation report
5. **Create Memo** - Investment recommendation with reasoning

Would you like me to help implement any of these components?
