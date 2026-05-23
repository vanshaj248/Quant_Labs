# Stock Return PCA Decomposition Dashboard

A full quantitative finance TUI application for decomposing portfolio risk into systematic, sector, and idiosyncratic components using Principal Component Analysis (PCA) via eigenvalue decomposition.

---

## Architecture

```
pca_dashboard/
├── .env                  ← API keys & config (edit before running)
├── dashboard.py          ← Textual/Rich TUI dashboard (main entry)
├── data_pipeline.py      ← Alpaca API + DuckDB/SQLite data layer
├── pca_engine.py         ← PCA via numpy.linalg.eigh + risk metrics
└── pca_portfolio.db      ← DuckDB-compatible SQLite database (auto-created)
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install numpy pandas scipy python-dotenv rich textual duckdb alpaca-py
```

> **DuckDB note:** The database layer is written in DuckDB-compatible SQL but falls back to `sqlite3` (Python built-in) automatically if `duckdb` is not installed. To use native DuckDB, replace the `sqlite3.connect(...)` line in `data_pipeline.py` with `duckdb.connect(...)`.

### 2. Configure API keys

Edit `.env`:
```
ALPACA_API_KEY=your_api_key_here
ALPACA_SECRET_KEY=your_secret_key_here
```

Get free keys at: https://alpaca.markets/

Without keys, the app generates **synthetic correlated returns** via a factor model (GBM simulation) so all analysis still works.

### 3. Run

```bash
cd pca_dashboard
python3 dashboard.py
```

**Keyboard controls:**
- `r` — Refresh data and re-run PCA  
- `q` — Quit

---

## What the App Does

### Data Pipeline (`data_pipeline.py`)

1. **Check DuckDB cache** — if prices for all 20 tickers exist in the DB and cover ≥ 60 days, skip API call
2. **Alpaca v2 multi-stock bars** — fetches 1-day OHLCV adjusted for splits via `GET /v2/stocks/bars`
3. **Synthetic fallback** — if keys are missing/invalid, generates correlated log-normal returns using a 3-factor GBM model (market + sector + idiosyncratic) ensuring meaningful PCA structure

### PCA Engine (`pca_engine.py`)

```
Daily log returns  r_t = log(P_t / P_{t-1})
Demean:            R_c = R - mean(R)
Covariance:        Σ = R_c'R_c / (T-1)       [N×N]
Eigendecompose:    Σ = V Λ V'                  (numpy.linalg.eigh)
Sort:              λ_1 ≥ λ_2 ≥ ... ≥ λ_N
Loadings:          L_k = v_k · √λ_k
Reconstruct:       Σ̂ = Σ_{k=1}^{K} λ_k v_k v_k'
Project:           S = R_c V_K               [T×K] factor scores
```

### Component Interpretation

| Component | Interpretation | Characteristics |
|-----------|---------------|-----------------|
| **PC1** | **Market / Systematic** | All loadings same sign; explains 50–70% of variance; beta-like exposure |
| **PC2** | **Sector / Style** | Opposing loadings across sector groups (e.g., Energy+ vs Tech−) |
| **PC3** | **Idiosyncratic** | Mixed/residual; stock-specific variance unexplained by macro factors |

### Portfolio Risk Decomposition

For equal-weight portfolio w = 1/N · **1**:

```
σ²_total    = w' Σ w
σ²_PC_k     = w' (λ_k v_k v_k') w
σ²_residual = σ²_total − Σ σ²_PC_k
```

Annualised volatility = √(σ² × 252) × 100%

---

## Database Schema

```sql
-- Price storage (DuckDB / SQLite compatible)
daily_prices (ticker, trade_date, open, high, low, close, volume, fetched_at)

-- PCA run metadata
pca_runs (run_id, run_at, n_stocks, n_components, lookback_days,
          explained_var, eigenvalues, loadings)

-- Per-component stock loadings
pca_components (run_id, component, ticker, loading)
```

---

## TUI Dashboard Panels

| Panel | Content |
|-------|---------|
| **Banner** | Stock count, lookback days, data source, run ID, timestamp |
| **Scree Plot** | Per-PC explained variance (top 10), cumulative totals |
| **Risk Decomposition** | Annualised vol by factor (PC1/PC2/PC3/residual) |
| **PC Loadings × 3** | Top-10 stocks by absolute loading, with sector and directional bars |
| **Cumulative Var** | Running sum of explained variance across all PCs |
| **Factor Vol Bar** | Each PC's vol contribution as % of total |
| **Correlation Heatmap** | ASCII heatmap of 12×12 asset correlation matrix |

---

## Configuration (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `ALPACA_API_KEY` | — | Alpaca API key (free tier works) |
| `ALPACA_SECRET_KEY` | — | Alpaca secret key |
| `ALPACA_BASE_URL` | `https://data.alpaca.markets` | API base URL |
| `DB_PATH` | `pca_portfolio.db` | SQLite/DuckDB file path |
| `LOOKBACK_DAYS` | `252` | Trading days of history (1 year) |
| `TOP_N_COMPONENTS` | `3` | PCs to extract (currently 3 hardcoded) |

---

## Extending to DuckDB

Replace the connection in `data_pipeline.py`:

```python
# Before (sqlite3 fallback)
import sqlite3
self.conn = sqlite3.connect(path)

# After (native DuckDB)
import duckdb
self.conn = duckdb.connect(path)
```

DuckDB enables columnar analytics queries like:

```sql
-- Correlation of PC loadings over time
SELECT component, ticker, AVG(loading) as avg_loading
FROM pca_components
GROUP BY component, ticker
ORDER BY component, ABS(avg_loading) DESC;
```

---

## Upgrading to Textual TUI

To use the full Textual framework (richer interactive widgets):

```bash
pip install textual
```

Then add `textual`-based widgets (DataTable, PlotextPlot, TabbedContent) to replace the `rich.Live` render loop in `dashboard.py`. The `pca_engine.py` and `data_pipeline.py` modules are framework-agnostic.
