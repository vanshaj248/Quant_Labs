# 📊 Company Valuation & Investment Dashboard

A terminal-based (TUI) dashboard for end-to-end company valuation.  
Covers **every M1 concept**: TVM, NPV/IRR, WACC, DCF, capital structure, and dividend analysis.

---

## 🚀 Quick Start

```bash
cd valuation_dashboard
cp .env.example .env   # or edit .env directly
# Fill in your API keys
./run.sh
```

Or directly:
```bash
python3 main.py
```

---

## 🔑 API Keys Required

| API | URL | Tier Needed |
|-----|-----|-------------|
| Alpaca | https://alpaca.markets | Free (paper trading) |
| Finnhub | https://finnhub.io | Free (60 req/min) |

Edit `.env`:
```
ALPACA_API_KEY=PKxxxxxxxxxxxxxxxx
ALPACA_SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FINNHUB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📐 M1 Concepts Covered

| Concept | Where in TUI |
|---------|-------------|
| **TVM** (PV/FV) | Tab: TVM / DCF |
| **NPV** | Tab: NPV / IRR |
| **IRR** | Tab: NPV / IRR |
| **WACC** | Tab: WACC / Capital |
| **CAPM** | Tab: WACC / Capital |
| **DCF Valuation** | Tab: TVM / DCF |
| **Terminal Value** | Tab: TVM / DCF |
| **Capital Structure** | Tab: WACC / Capital |
| **Intrinsic vs Market** | Tab: Valuation |
| **Sensitivity Analysis** | Tab: Sensitivity |
| **Dividend Policy** | Tab: Dividends |

---

## 🖥️ TUI Navigation

| Key | Action |
|-----|--------|
| `A` | Add a new company |
| `R` | Refresh data for current company |
| `V` | Re-run valuation calculations |
| `Q` | Quit |
| `Tab` | Switch between panels |
| Click | Select company in sidebar |

---

## 🗄️ Database Structure

Each company gets its own DuckDB file:
```
databases/
  AAPL.duckdb
  MSFT.duckdb
  INFY.duckdb
  ...
```

Tables per database:
- `company_profile` — name, exchange, market cap, etc.
- `price_history` — daily OHLCV bars
- `financials` — income/cash flow data
- `metrics` — 80+ Finnhub financial ratios
- `valuation` — timestamped DCF results
- `dividends` — historical dividend payments
- `peers` — sector peer tickers

---

## 📐 Financial Formulas

### TVM
```
PV  = FV / (1 + r)^n
FV  = PV × (1 + r)^n
```

### CAPM
```
Ke = Rf + β × (Rm - Rf)
```

### WACC
```
WACC = (E/V) × Ke + (D/V) × Kd × (1 - t)
```

### DCF
```
EV = Σ FCFt/(1+WACC)^t + TV/(1+WACC)^n
TV = FCFn × (1+g) / (WACC - g)     [Gordon Growth]
```

### NPV / IRR
```
NPV = -C₀ + Σ CFt / (1+r)^t
IRR: solve NPV = 0
```

---

## 🏗️ File Structure

```
valuation_dashboard/
├── main.py           # TUI app (Textual)
├── data_fetcher.py   # Alpaca + Finnhub API calls
├── db_manager.py     # DuckDB per-company storage
├── finance_calc.py   # All financial math (TVM/DCF/NPV/IRR/WACC)
├── run.sh            # Launcher script
├── .env              # API keys (NOT committed to git)
└── databases/        # Auto-created DuckDB files
    └── *.duckdb
```

---

## 📦 Dependencies

```
textual        # TUI framework
duckdb         # Embedded database
requests       # HTTP client
python-dotenv  # .env loading
finnhub-python # Finnhub SDK
```

Install: `pip install textual duckdb requests python-dotenv finnhub-python`
