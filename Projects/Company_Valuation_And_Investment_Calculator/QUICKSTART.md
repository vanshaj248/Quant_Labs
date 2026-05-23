# Quick Start Guide 🚀

## Installation (30 seconds)

```bash
cd Company_Valuation_And_Investment_Calculator
pip install finnhub-python textual duckdb numpy
echo 'FINNHUB_API_KEY=d88c5lpr01qq4342i490d88c5lpr01qq4342i49g' > .env
```

## Run Modes

### 1️⃣ **Interactive TUI** (Recommended)
```bash
python main.py
```
- Browse companies from database
- View DCF valuations
- Run sensitivity analysis
- Export reports

**Controls:**
- `↑/↓` - Navigate companies
- `Enter` - Select company
- `q` - Quit

---

### 2️⃣ **Demo Mode** (See All Features)
```bash
python demo.py
```
Shows:
- ✓ TVM calculations (PV, FV, IRR, NPV)
- ✓ WACC estimation (CAPM, cost of debt)
- ✓ DCF valuation (5-year projections)
- ✓ DuckDB database with 10 NASDAQ companies

**Output:** Formatted financial analysis with formulas and results

---

### 3️⃣ **Initialize Database**
```bash
python main.py --init
```
Creates DuckDB with:
- 10 pre-loaded NASDAQ companies
- 5-table schema (companies, financials, market_data, valuations, dividends)
- Ready for data ingestion

---

### 4️⃣ **Ingest Financial Data**
```bash
# Fetch top 5 companies
python main.py --ingest

# Fetch specific companies
python main.py --ingest AAPL MSFT GOOGL NVDA
```
Fetches from Finnhub:
- Company profile & metrics
- Financial statements
- Price quotes
- Earnings data

Stores in DuckDB (not Excel)

---

### 5️⃣ **Single Company Valuation**
```bash
python main.py --valuate AAPL
```
Prints detailed DCF report:
- Current price vs intrinsic value
- WACC breakdown
- 5-year FCF projections
- Investment recommendation

---

## Complete Workflow

```bash
# Step 1: Initialize (one-time)
python main.py --init
# Output: ✓ Database initialized with Top 10 NASDAQ companies

# Step 2: Fetch data for companies of interest
python main.py --ingest AAPL MSFT GOOGL
# Output: Fetching [AAPL]... ✓ Complete

# Step 3: View valuations in TUI
python main.py
# Output: Interactive terminal UI opens

# Or: View single company report
python main.py --valuate MSFT
# Output: Detailed DCF valuation report
```

---

## Example Output

```
======================================================================
  DCF VALUATION ANALYSIS - AAPL
======================================================================

📊 Fetching market data...
  ✓ Current Price: $182.52
  ✓ Market Cap: $2,850,000M
  ✓ Beta: 1.08

💰 Calculating WACC...
  ✓ Cost of Equity (CAPM): 12.56%
  ✓ Cost of Debt: 2.06%
  ✓ WACC: 12.16%

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
```

---

## Key Features

### 📊 TVM Calculator
- Present Value (PV)
- Future Value (FV)
- Annuities
- NPV & IRR
- Perpetuity

### 💰 WACC Calculation
- CAPM Cost of Equity
- Cost of Debt
- Capital structure weights
- Tax effects

### 📈 DCF Model
- 5-year projections
- Terminal value
- Sensitivity analysis
- Margin of safety

### 🗄️ DuckDB Storage
- No Excel files
- Company-centric schema
- 5 normalized tables
- Easy querying

### 🖥️ Interactive TUI
- Real-time navigation
- Company selector
- Valuation display
- Data export

---

## Common Commands

```bash
# See all features
python demo.py

# Launch interactive app
python main.py

# Initialize database (one-time)
python main.py --init

# Ingest data for Apple, Microsoft, Google
python main.py --ingest AAPL MSFT GOOGL

# Valuate Tesla
python main.py --valuate TSLA

# Check database
python -c "from src.database.init_db import CompanyDatabase; db = CompanyDatabase(); print(db.get_all_companies()); db.close()"
```

---

## Troubleshooting

### Error: "No module named 'finnhub'"
```bash
pip install finnhub-python
```

### Error: ".env file not found"
```bash
echo 'FINNHUB_API_KEY=your_key_here' > .env
```

### Error: "Database not initialized"
```bash
python main.py --init
```

### API limit exceeded
- Finnhub free tier: 60 API calls/minute
- Ingestion automatically adds delays
- Premium tier: unlimited calls

---

## Next Steps

1. **Run demo.py** to see all features in action
2. **Run main.py --init** to initialize database
3. **Run main.py --ingest AAPL** to fetch real data
4. **Run main.py** to launch interactive UI
5. **Run main.py --valuate GOOGL** to see DCF report

---

## Project Structure

```
Company_Valuation_And_Investment_Calculator/
├── main.py                    # Entry point
├── demo.py                    # Feature showcase
├── .env                       # API keys
├── Readme.md                  # Full documentation
├── data/
│   └── company_valuations.duckdb
├── src/
│   ├── valuation/
│   │   ├── tvm.py            # Time value of money
│   │   ├── wacc.py           # Cost of capital
│   │   └── dcf.py            # DCF model
│   ├── database/
│   │   └── init_db.py        # DuckDB schema
│   ├── ingestion/
│   │   └── ingestion.py      # Finnhub pipeline
│   ├── tui.py                # Interactive interface
│   └── valuation_engine.py   # Orchestrator
└── test/
    ├── finnhub_pipeline.py
    └── Run.py
```

---

**Happy Valuing! 📊💰**

For questions or issues, check the main README.md file.
