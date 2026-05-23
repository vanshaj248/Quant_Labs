# DCF Valuation Analyzer 📊

A comprehensive financial analysis tool for performing DCF (Discounted Cash Flow) valuation on public companies. Combines **TVM calculations**, **WACC estimation**, **5-year FCF projections**, and **NPV/IRR analysis** with an interactive **TUI interface**.

## Features

### 1. **Time Value of Money (TVM) Calculator** ⏰
- Present Value (PV) and Future Value (FV) calculations
- Discount cash flows using WACC
- Terminal value computation using perpetuity growth formula
- IRR and NPV analysis for project evaluation

### 2. **WACC (Weighted Average Cost of Capital)** 💰
- **Cost of Equity** calculation using CAPM:
  - `Re = Rf + β(Rm - Rf)`
  - Risk-free rate: 4.5% (10-year Treasury)
  - Market risk premium: 6.5% (historical average)
  
- **Cost of Debt** from financial statements:
  - `Rd = (Interest Expense / Total Debt) × (1 - Tax Rate)`
  
- **WACC** combining both:
  - `WACC = (E/V)×Re + (D/V)×Rd×(1-Tc)`

### 3. **DCF Valuation Model** 📈
- 5-year FCF projections with declining growth rates
- Terminal value using perpetuity growth (2.5% default)
- Intrinsic value per share calculation
- Margin of safety analysis
- Valuation recommendation (STRONG BUY / BUY / HOLD / SELL)

### 4. **Project NPV & IRR Analysis** 🎯
- Evaluate hypothetical new projects
- Calculate Net Present Value (NPV)
- Compute Internal Rate of Return (IRR)
- Compare IRR vs WACC for project acceptance

### 5. **Company Comparison** 📊
- Analyze Top 10 NASDAQ companies
- Dividend policy analysis
- Dividend yield comparison vs peers
- Peer valuation metrics

### 6. **DuckDB Storage** 🗄️
Company-wise data storage (not Excel):
- **companies** - Company profiles & metadata
- **financials** - Annual income statements, balance sheets, cash flows
- **market_data** - Daily OHLCV price data
- **valuations** - DCF results & metrics
- **dividends** - Dividend history & yields

### 7. **Interactive TUI** 🖥️
Built with **textual** framework:
- Company selector from database
- Real-time valuation display
- Sensitivity analysis tables
- Export reports
- Data ingestion controls

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone/navigate to project
cd Company_Valuation_And_Investment_Calculator

# Install dependencies
pip install finnhub-python textual duckdb numpy pandas requests

# Setup environment variables
echo 'FINNHUB_API_KEY=your_api_key_here' >> .env
```

Get your Finnhub API key from: https://finnhub.io/dashboard/api-token

## Usage

### 1. **Interactive TUI Mode** (Default)
```bash
python main.py
```
Launches the interactive terminal interface where you can:
- Browse Top 10 NASDAQ companies
- View DCF valuations
- Perform sensitivity analysis
- Export reports

### 2. **Initialize Database**
```bash
python main.py --init
```
Creates DuckDB schema and adds top 10 NASDAQ companies:
- AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, BRK.B, JPM, V

### 3. **Ingest Financial Data**
```bash
# Ingest top 5 companies
python main.py --ingest

# Ingest specific companies
python main.py --ingest AAPL MSFT GOOGL
```

### 4. **Run Single Valuation**
```bash
python main.py --valuate AAPL
```

Output example:
```
======================================================================
  DCF VALUATION ANALYSIS - AAPL
======================================================================

📊 Fetching market data...
  ✓ Current Price: $182.52
  ✓ Market Cap: $2,850,000M
  ✓ Beta: 1.24

💰 Calculating WACC...
  ✓ Cost of Equity (CAPM): 10.56%
  ✓ Cost of Debt: 3.25%
  ✓ WACC: 9.82%

📈 Projecting Free Cash Flows...
  ✓ 5-Year Projections:
    Year 1: $120,000M
    Year 2: $134,400M
    Year 3: $147,840M
    Year 4: $159,667M
    Year 5: $167,650M

🎯 Running DCF Valuation...

======================================================================
  VALUATION RESULTS
======================================================================

Ticker: AAPL
Current Market Price: $182.52
Intrinsic Value (DCF): $195.75
Margin of Safety: +7.2%

Recommendation: BUY

Upside: +7.2%

======================================================================
DCF Components:
  PV of FCFs (Years 1-5): $550,000M
  Terminal Value: $2,800,000M
  PV of Terminal Value: $1,620,000M
  Enterprise Value: $2,170,000M
  Equity Value: $2,150,000M
======================================================================
```

## Project Structure

```
Company_Valuation_And_Investment_Calculator/
├── main.py                          # Entry point
├── .env                             # API keys & config
├── data/
│   └── company_valuations.duckdb    # DuckDB database
├── src/
│   ├── valuation/
│   │   ├── tvm.py                   # Time Value of Money
│   │   ├── wacc.py                  # WACC calculation
│   │   ├── dcf.py                   # DCF valuation
│   │   └── __init__.py
│   ├── database/
│   │   ├── init_db.py               # DuckDB schema & setup
│   │   └── __init__.py
│   ├── ingestion/
│   │   ├── ingestion.py             # Finnhub data pipeline
│   │   └── __init__.py
│   ├── valuation_engine.py          # Integrated valuation engine
│   ├── tui.py                       # Textual TUI interface
│   └── __init__.py
├── test/
│   ├── finnhub_pipeline.py          # Finnhub API client
│   ├── Run.py                       # CLI runner
│   └── Example usage.py
└── README.md
```

## Valuation Theory

### DCF Formula
```
Intrinsic Value = Σ[FCFt / (1 + WACC)^t] + [TV / (1 + WACC)^n]

where:
  FCFt = Free Cash Flow in year t
  WACC = Weighted Average Cost of Capital
  TV = Terminal Value = FCF_final × (1 + g) / (WACC - g)
  g = Perpetual growth rate (2.5%)
  n = Number of projection years (5)
```

### Valuation Decision Rules
- **Margin of Safety > 20%** → STRONG BUY
- **Margin of Safety > 10%** → BUY
- **Margin of Safety ±10%** → HOLD
- **Margin of Safety < -20%** → STRONG SELL

### NPV & IRR Analysis
```
NPV = Σ[CFt / (1 + WACC)^t] - Initial Investment

IRR is the discount rate where NPV = 0
Decision: Accept project if IRR > WACC
```

## Key Assumptions

- **Risk-free rate**: 4.5% (US 10-year Treasury)
- **Market risk premium**: 6.5% (historical average)
- **Tax rate**: 25% (adjustable)
- **Terminal growth rate**: 2.5% (perpetuity)
- **FCF growth rates**: [15%, 12%, 10%, 8%, 5%] (declining)

## Database Schema

### companies
```sql
- ticker (PK): AAPL
- name: Apple Inc
- sector: Technology
- industry: Consumer Electronics
- country: USA
- market_cap: 2850000
- website: https://www.apple.com
```

### financials
```sql
- ticker: AAPL
- fiscal_year: 2023
- revenue: 394328
- net_income: 99803
- free_cash_flow: 110543
- total_debt: 106589
- shares_outstanding: 15552
```

### valuations
```sql
- ticker: AAPL
- valuation_date: 2024-05-23
- current_price: 182.52
- intrinsic_value_per_share: 195.75
- margin_of_safety: 0.072
- recommendation: BUY
- wacc: 0.0982
- dcf_data: {...full calculation details...}
```

## Examples

### Quick Valuation
```python
from src.valuation_engine import CompanyValuationEngine

engine = CompanyValuationEngine(api_key="your_api_key")
valuation = engine.run_valuation("AAPL")
engine.print_valuation_report(valuation)
engine.close()
```

### TVM Calculations
```python
from src.valuation.tvm import TVMCalculator

# PV of $1000 in 5 years at 10% discount rate
pv = TVMCalculator.pv_single(fv=1000, rate=0.10, periods=5)
print(f"PV: ${pv:.2f}")  # ~$620.92

# Discount a series of cash flows
cfs = [100, 200, 300, 400, 500]
discounted, total_pv = TVMCalculator.discount_cash_flows(cfs, 0.10)
print(f"Total PV: ${total_pv:.2f}")
```

### WACC Estimation
```python
from src.valuation.wacc import WACCCalculator

wacc_data = WACCCalculator.estimate_wacc(
    market_cap=2850000,        # $2.85T
    total_debt=106589,          # $106.6B
    interest_expense=2931,      # $2.931B
    beta=1.24,
    tax_rate=0.25
)

print(f"WACC: {wacc_data.wacc*100:.2f}%")
print(f"Cost of Equity: {wacc_data.cost_of_equity*100:.2f}%")
print(f"Cost of Debt: {wacc_data.cost_of_debt*100:.2f}%")
```

## Data Sources

- **Finnhub API**: Company financials, quotes, metrics, earnings
- **Company Financials**: Annual reports, SEC filings
- **Market Data**: Real-time prices, historical OHLCV
- **Risk-free Rate**: US Treasury yields
- **Market Risk Premium**: Historical S&P 500 returns

## Limitations & Assumptions

1. **FCF Projections** are estimated based on historical growth trends
2. **Terminal Growth Rate** is assumed constant at 2.5%
3. **Beta** is from Finnhub; may not reflect future volatility
4. **Tax Rate** is fixed at 25%; actual varies by company
5. **Market Risk Premium** uses historical average; actual may differ
6. **One-year lag** in financial data from SEC filings

## Future Enhancements

- [ ] Multi-scenario analysis (bull/base/bear cases)
- [ ] Peer comparison dashboard
- [ ] Historical valuation tracking
- [ ] Monte Carlo simulation
- [ ] Dividend discount model (DDM)
- [ ] Free cash flow to equity (FCFE) model
- [ ] Export to PDF reports
- [ ] Real-time price alerts
- [ ] Portfolio analysis

## Contributing

Contributions welcome! Areas of interest:
- Additional valuation models (DDM, Comparable Company Analysis)
- Enhanced TUI interface
- More data sources integration
- Performance optimizations

## License

MIT License - See LICENSE file for details

## Author

Built with ❤️ for financial analysis enthusiasts

## References

- Damodaran, A. (2023). "Valuation: Measuring and Managing the Value of Companies"
- Graham, B., & Dodd, D. L. (1934). "Security Analysis"
- Ross, S. A., Westerfield, R. W., & Jordan, B. D. (2013). "Fundamentals of Corporate Finance"

## Support

For issues, questions, or suggestions:
- Check existing documentation
- Review example usage files
- Examine database schema
- Test with --init and --ingest first

---

**Happy Valuing! 📊💰**
