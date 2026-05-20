# Quantitative Finance Roadmap
### July 2026 – March 2027 · 9 Months · 10 Modules + 10 Mini Projects + 1 Capstone

---

## Overview

| Detail | Info |
|---|---|
| **Duration** | July 2026 – March 2027 (9 months) |
| **Total Modules** | 10 Core Modules |
| **Projects** | 10 Module Mini Projects + 1 Capstone |
| **Target Roles** | Risk Manager, Portfolio Manager, Quantitative Consultant |
| **Background** | Designed for STEM students with no prior finance background |

---

## Phases at a Glance

| Phase | Period | Focus |
|---|---|---|
| **Phase 1 · Foundation** | July – August 2026 | Finance basics, accounting, valuation |
| **Phase 2 · Core Quant** | September – November 2026 | Math, Python, investments, portfolio theory |
| **Phase 3 · Advanced** | December 2026 – March 2027 | Derivatives, risk, fixed income, quant strategies |

---

## Phase 1 · Foundation
> *Build the financial intuition before diving into quantitative methods.*

---

### M1 · Finance Fundamentals
**Month:** July 2026 · **Duration:** 3 weeks study + 1 week project

**Goal:** Understand the basics of finance, instruments, markets, and time value of money.

**Topics:**
- Financial systems, institutions, and markets
- Time value of money (NPV, IRR)
- Discounting and compounding
- Bonds, stocks, mutual funds, ETFs
- Capital structure and cost of capital
- Corporate valuation and dividend policies

**📘 Book:** *Principles of Corporate Finance* – Richard Brealey & Stewart Myers

#### 🎯 Mini Project M1 · Company Valuation & Investment Calculator

**Goal:** Apply every M1 concept — TVM, NPV/IRR, capital structure, and valuation — to analyse and value a real listed company end to end.

**Tasks:**
- Pick any Nifty 50 / S&P 500 company (e.g. Infosys, Apple)
- Build a TVM calculator: compute PV and FV of projected free cash flows using manual discounting formulas
- Estimate the company's WACC using its capital structure (debt/equity ratio, cost of debt from financials, CAPM for cost of equity)
- Run a DCF valuation: discount 5-year projected FCFs + terminal value at WACC to get intrinsic value per share
- Compute NPV of a hypothetical new project the company could undertake; find IRR and compare with WACC
- Compare intrinsic value against current market price — is the stock over/undervalued?
- Summarise the company's dividend policy and compare its dividend yield with peers

**Topics Covered:** TVM · NPV · IRR · WACC · Capital structure · DCF valuation · Dividend policy

**✅ Deliverable:** Excel or Python notebook — DCF model with WACC build-up, NPV/IRR analysis, and a 1-page investment memo (Buy / Hold / Sell recommendation with reasoning).

---

### M2 · Financial Accounting & Statement Analysis
**Month:** August 2026 · **Duration:** 3 weeks study + 1 week project

**Goal:** Learn to read, interpret, and analyze financial statements.

**Topics:**
- Balance sheet, income statement, cash flow statement
- Financial ratios (liquidity, profitability, leverage)
- Common-size analysis
- Earnings quality and red flags
- Valuation multiples (P/E, EV/EBITDA)

**📘 Book:** *Financial Statement Analysis* – Martin Fridson

#### 🎯 Mini Project M2 · Financial Health Screener

**Goal:** Build a multi-company financial screener that reads, analyses, and scores companies purely from their financial statements.

**Tasks:**
- Download 3 years of annual financials for 10 companies in the same sector (e.g. Indian IT or US banks) using `yfinance` or manual scraping
- Parse the income statement, balance sheet, and cash flow statement for each company
- Compute a full ratio dashboard: Current Ratio, Quick Ratio, Debt-to-Equity, Interest Coverage, ROE, ROA, Net Profit Margin, Asset Turnover
- Run common-size analysis: express every income statement line as % of revenue and every balance sheet line as % of total assets; spot structural differences across companies
- Flag earnings quality red flags: large gap between net income and operating cash flow, rising receivables faster than revenue, aggressive accruals
- Compute P/E, EV/EBITDA, P/B, and P/FCF multiples for each company
- Score and rank all 10 companies on a composite financial health score (weighted average of ratios)

**Topics Covered:** All three statements · Liquidity, profitability & leverage ratios · Common-size analysis · Earnings quality · Valuation multiples

**✅ Deliverable:** Python notebook + auto-generated PDF report with ratio tables, common-size charts, red flag alerts, and a ranked leaderboard of the 10 companies.

---

## Phase 2 · Core Quant
> *Build the mathematical toolkit and apply it in Python alongside investment theory.*

---

### M3 · Quantitative Methods for Finance
**Month:** September 2026 · **Duration:** 3 weeks study + 1 week project

**Goal:** Build math skills for modeling, risk, and asset pricing.

**Topics:**
- Linear algebra (matrices, eigenvalues, decomposition)
- Probability and distributions (normal, binomial, lognormal)
- Statistical inference (t-tests, p-values, confidence intervals)
- Time series analysis (AR, MA, ARIMA)
- Optimization (Lagrange, convex programming)

**📘 Book:** *Mathematics for Economists* – Simon & Blume

#### 🎯 Mini Project M3 · Quant Toolkit: From Matrices to Forecasts

**Goal:** Apply every M3 technique to a single dataset of stock returns — demonstrating how each mathematical tool answers a different financial question.

**Tasks:**
- **Linear Algebra:** Build the covariance matrix of 10 stock returns. Compute eigenvalues and eigenvectors. Run PCA and extract the top 3 components — interpret them as market, sector, and idiosyncratic risk
- **Probability:** Fit a Normal and a Student-t distribution to daily returns. Test normality (Jarque-Bera). Compute the probability of a loss exceeding 3% on any given day
- **Statistical Inference:** Run a t-test to check whether the mean return of a stock is statistically different from zero. Build 95% confidence intervals for the mean and variance of returns
- **Time Series:** Test for stationarity (ADF test). Fit an ARIMA model to a stock's return series. Produce a 20-day return forecast with confidence bands
- **Optimization:** Use convex optimization (CVXPY) to find the portfolio weights that minimize variance subject to a target return constraint — Lagrange multiplier approach

**Topics Covered:** Linear algebra · PCA · Distributions · Hypothesis testing · ARIMA · Convex optimization

**✅ Deliverable:** Single structured Jupyter notebook with 5 clearly labelled sections — one per math tool — all applied to the same dataset, with financial interpretation for every result.

---

### M9 · Python for Quantitative Finance *(Parallel Track)*
**Month:** September – October 2026 · **Duration:** Ongoing parallel track

**Goal:** Apply programming to finance problems and automate analysis.

> 💡 *Run this track alongside M3–M5 to implement every concept you learn in code.*

**Topics:**
- Data handling with Pandas and NumPy
- Financial APIs (yfinance, Alpha Vantage)
- Portfolio optimization with CVXPY
- Backtesting strategies (bt, Pyfolio)
- Web dashboards with Streamlit

**📘 Book:** *Python for Finance* – Yves Hilpisch

#### 🎯 Mini Project M9 · Personal Finance Analytics Dashboard

**Goal:** Build a fully functional Streamlit web app that pulls live data and provides end-to-end portfolio analytics — covering every M9 tool.

**Tasks:**
- **Data & APIs:** Pull 2 years of daily price data for a 5-asset portfolio using `yfinance`; clean and align using Pandas; compute log returns with NumPy
- **Portfolio Analytics:** Compute rolling mean return, rolling volatility, and rolling Sharpe ratio (252-day window) using vectorised Pandas operations
- **Optimization:** Run mean-variance optimization with CVXPY to find the max-Sharpe portfolio; display optimal weights
- **Backtesting:** Implement a simple momentum strategy (buy top-3 performers of last month) using `bt`; generate a Pyfolio tear sheet with drawdown, rolling beta, and monthly return heatmap
- **Dashboard:** Wrap everything in a Streamlit app with sidebar controls (date range, asset selector, risk-free rate slider) that updates all charts live

**Topics Covered:** Pandas · NumPy · yfinance API · CVXPY optimization · bt backtesting · Pyfolio · Streamlit

**✅ Deliverable:** Deployed Streamlit app (or localhost demo) with live data, interactive controls, portfolio analytics, and a downloadable backtest report.

---

### M4 · Investments & Asset Pricing
**Month:** October 2026 · **Duration:** 3 weeks study + 1 week project

**Goal:** Understand how assets are priced and how to evaluate returns.

**Topics:**
- CAPM, APT, Fama-French three-factor model
- Efficient Market Hypothesis (EMH)
- Risk and return framework
- Sharpe, Treynor, and Sortino ratios
- Behavioral finance overview

**📘 Book:** *Investments* – Bodie, Kane & Marcus

#### 🎯 Mini Project M4 · Asset Pricing & Market Efficiency Analyser

**Goal:** Test whether real markets price assets as theory predicts — using CAPM, Fama-French, and EMH tests on actual data.

**Tasks:**
- **CAPM:** Estimate beta for 10 stocks by regressing excess returns on market excess returns. Plot the Security Market Line. Identify which stocks plot above (underpriced) and below (overpriced) the SML
- **Fama-French:** Download FF3 factor data. Regress each stock on market, SMB, and HML factors. Compare R² vs plain CAPM — does FF3 explain more of the return variation?
- **APT:** Add a custom macro factor (e.g. INR/USD or oil price) to the regression. Test if it carries a significant risk premium
- **EMH Test:** Run autocorrelation tests on daily returns (Ljung-Box test). Test whether past 5-day returns predict next-day returns. Discuss what the result implies about market efficiency
- **Performance Ratios:** Compute Sharpe, Treynor, and Sortino for each stock. Rank them. Show that a high Sharpe stock doesn't necessarily have a high Treynor ratio (explain why with beta)
- **Behavioral Finance:** Plot the disposition effect — using trade data or a simulation, show that investors hold losers too long and sell winners too early

**Topics Covered:** CAPM · SML · APT · Fama-French · EMH · Sharpe/Treynor/Sortino · Behavioral bias

**✅ Deliverable:** Notebook with SML plot, factor regression table, EMH autocorrelation test results, performance ratio ranking, and a 1-page discussion of what the tests imply about market efficiency.

---

### M5 · Portfolio Theory & Construction
**Month:** November 2026 · **Duration:** 2.5 weeks study + 1.5 weeks project

**Goal:** Build optimal portfolios based on risk-return tradeoffs.

**Topics:**
- Mean-variance optimization
- Efficient frontier construction
- Capital Market Line (CML) and Security Market Line (SML)
- Factor models and alpha/beta separation
- Portfolio rebalancing and performance attribution

**📘 Book:** *Quantitative Investment Analysis* – CFA Institute

#### 🎯 Mini Project M5 · Full Portfolio Construction & Attribution Engine

**Goal:** Go from raw price data to a fully optimised, rebalanced portfolio with complete performance attribution — covering every M5 concept.

**Tasks:**
- **Mean-Variance Optimization:** Select 12 assets (equities, bonds, gold, REITs). Compute expected returns and covariance matrix. Use CVXPY to solve: (a) minimum variance, (b) maximum Sharpe, (c) target return portfolios under long-only constraints
- **Efficient Frontier:** Plot 5,000 random portfolios (Monte Carlo) alongside the true efficient frontier. Mark the minimum-variance and max-Sharpe portfolios. Draw the Capital Market Line
- **Factor Decomposition:** Run Fama-French regression on the optimal portfolio. Decompose total return into: market beta return, SMB/HML factor return, and alpha (stock-picking skill)
- **Rebalancing Simulation:** Run a 2-year backtest with monthly calendar rebalancing vs 5%-drift threshold rebalancing. Compare turnover, transaction costs (assume 10bps/trade), and net Sharpe ratio
- **Performance Attribution:** Break down the portfolio's active return vs benchmark into: asset allocation effect, security selection effect, and interaction effect (Brinson model)

**Topics Covered:** Mean-variance · Efficient frontier · CML · Factor models · Alpha/beta · Rebalancing · Performance attribution

**✅ Deliverable:** Interactive efficient frontier chart + Brinson attribution table + rebalancing comparison report. All in a single Jupyter notebook.

---

## Phase 3 · Advanced
> *Master derivatives, risk frameworks, fixed income, and systematic strategy development.*

---

### M6 · Derivatives & Financial Engineering
**Month:** December 2026 · **Duration:** 3 weeks study + 1 week project

**Goal:** Understand and model derivatives — options, futures, and swaps.

**Topics:**
- Futures, forwards, options, and swaps
- Arbitrage and hedging strategies
- Binomial option pricing model
- Black-Scholes-Merton (BSM) model
- Greeks: Delta, Gamma, Vega, Theta
- Introduction to exotic options

**📘 Book:** *Options, Futures and Other Derivatives* – John C. Hull

#### 🎯 Mini Project M6 · Derivatives Pricing & Hedging Simulator

**Goal:** Price every major derivative type from scratch and build a live Greeks dashboard — covering the full M6 syllabus.

**Tasks:**
- **Forwards & Futures:** Price a 6-month forward on a stock with known dividends. Verify the no-arbitrage forward price. Simulate a futures P&L using daily mark-to-market over the contract life
- **Swaps:** Build a fixed-for-floating interest rate swap pricer. Compute the fixed rate that makes the swap fair (NPV = 0) at initiation. Show how the swap's mark-to-market value changes as interest rates move
- **Binomial Model:** Implement a 3-step binomial tree for a European and American put. Show early-exercise premium for the American put. Compare with BSM price
- **Black-Scholes-Merton:** Implement BSM from scratch. Price calls and puts across a grid of strikes (80% to 120% moneyness) and maturities (1M to 1Y). Plot the option price surface
- **Greeks Dashboard:** Compute Delta, Gamma, Vega, Theta analytically. Build a Streamlit app where the user inputs S, K, T, r, σ and sees all Greeks update in real time with a P&L heatmap for a delta-hedged position
- **Exotic Options:** Price an Asian (average price) call and a barrier knock-out call using Monte Carlo simulation (10,000 paths). Compare with vanilla BSM price

**Topics Covered:** Forwards · Futures · Swaps · Binomial model · BSM · All Greeks · Exotic options

**✅ Deliverable:** Streamlit Greeks dashboard + Jupyter notebook with all pricing models, option surface plot, and Monte Carlo exotic option pricer.

---

### M7 · Risk Management
**Month:** January 2027 · **Duration:** 3 weeks study + 1 week project

**Goal:** Measure and manage financial risks across market, credit, and operational dimensions.

**Topics:**
- Types of risk: market, credit, operational, liquidity
- Value at Risk (VaR) and Conditional VaR (CVaR)
- Stress testing and scenario analysis
- Credit scoring and PD/LGD modeling
- Basel II/III regulatory frameworks

**📘 Book:** *Risk Management and Financial Institutions* – John C. Hull

#### 🎯 Mini Project M7 · Enterprise Risk Dashboard

**Goal:** Build a comprehensive risk measurement system covering market, credit, and regulatory risk — every M7 topic in one integrated project.

**Tasks:**
- **Market Risk — VaR & CVaR:** For a 5-asset portfolio, compute 1-day VaR at 95% and 99% using (a) historical simulation, (b) parametric normal, (c) Monte Carlo with 50,000 paths. Compare all three. Compute CVaR (Expected Shortfall) for each method
- **Backtesting VaR:** Run a rolling 252-day VaR backtest. Count and plot VaR breaches. Apply Basel traffic-light test: green (<5 breaches), yellow (5–9), red (10+). Discuss what a red flag implies for capital requirements
- **Stress Testing:** Run 3 historical scenarios — 2008 GFC, 2020 COVID crash, 2022 rate hike shock. Apply the factor shocks to the portfolio and compute the P&L impact. Design 1 hypothetical scenario (e.g. India–Pakistan conflict shock)
- **Credit Risk — PD/LGD:** Use a public credit dataset (e.g. Lending Club or RBI data). Build a logistic regression model to predict Probability of Default (PD). Estimate LGD using historical recovery rates. Compute Expected Loss (EL = PD × LGD × EAD) for each loan
- **Liquidity Risk:** Compute bid-ask spread-adjusted VaR and Liquidity-Adjusted VaR (LVaR) for the portfolio. Show how illiquid assets inflate the true risk
- **Basel III Summary:** Map each risk calculation to its Basel III capital requirement equivalent. Compute a simplified Tier 1 Capital Ratio for a hypothetical bank

**Topics Covered:** Market/credit/liquidity/operational risk · VaR · CVaR · Stress testing · PD/LGD · Basel III

**✅ Deliverable:** Streamlit risk dashboard showing VaR, CVaR, stress test P&L, credit scorecard, and Basel capital summary — all updating from a shared portfolio input.

---

### M8 · Fixed Income & Credit Analytics
**Month:** February 2027 · **Duration:** 3 weeks study + 1 week project

**Goal:** Analyze bond markets, interest rate dynamics, and credit risk models.

**Topics:**
- Bond pricing, yield to maturity (YTM), duration, convexity
- Term structure of interest rates
- Spot rates and forward rates
- Credit risk models: structural vs reduced-form
- Securitization, MBS, and ABS

**📘 Book:** *Fixed Income Securities* – Bruce Tuckman & Angel Serrat

#### 🎯 Mini Project M8 · Fixed Income Analytics Suite

**Goal:** Build a complete fixed income toolkit — from pricing a single bond to modelling the entire yield curve and credit spreads.

**Tasks:**
- **Bond Pricing & Sensitivities:** Price a 10-year government bond at par, premium, and discount. Compute YTM via Newton-Raphson root finding. Calculate Macaulay duration, modified duration, and convexity. Use duration+convexity to estimate price impact of a 100bps parallel shift in rates. Compare with exact repricing
- **Yield Curve Bootstrapping:** Use Indian G-Sec or US Treasury market prices (3M to 30Y) to bootstrap the spot rate curve. Derive the forward rate curve. Plot both and identify where the curve is inverted or humped
- **Term Structure Models:** Fit the Nelson-Siegel model to the bootstrapped spot curve. Interpret the three factors (level, slope, curvature). Simulate curve evolution over 6 months using a simple Vasicek model
- **Credit Risk — Structural Model:** Implement a simplified Merton model. Treat equity as a call option on firm assets. Use BSM to back out implied asset value and volatility from equity price and volatility. Compute distance to default and PD
- **Credit Risk — Reduced Form:** Model default intensity (hazard rate) as a constant. Use it to price a 5-year Credit Default Swap (CDS). Back out the implied hazard rate from observed CDS spreads
- **Securitization:** Build a simple 3-tranche ABS model (senior, mezzanine, equity). Simulate monthly cash flows from an underlying loan pool. Apply waterfall rules to allocate principal and interest. Compute yield and duration for each tranche

**Topics Covered:** Bond pricing · YTM · Duration · Convexity · Spot/forward rates · Nelson-Siegel · Merton model · CDS pricing · ABS waterfall

**✅ Deliverable:** Python notebook — bond pricing engine + bootstrapped yield curve + Merton PD calculator + CDS pricer + 3-tranche ABS cashflow model with tranche yield table.

---

### M10 · Quantitative Research & Strategy Development
**Month:** February – March 2027 · **Duration:** 3 weeks study + 1 week project

**Goal:** Build systematic investment strategies and conduct quantitative alpha research.

**Topics:**
- Statistical arbitrage
- Momentum and mean-reversion strategies
- Smart beta and factor investing
- Machine learning applications in finance
- Backtesting pitfalls and performance evaluation

**📘 Book:** *Advances in Financial Machine Learning* – Marcos López de Prado

#### 🎯 Mini Project M10 · Multi-Strategy Alpha Research Platform

**Goal:** Research, implement, and rigorously evaluate three distinct systematic strategies — covering the full M10 curriculum in one unified platform.

**Tasks:**
- **Statistical Arbitrage (Pairs Trading):** Identify cointegrated pairs from a universe of 50 stocks using the Engle-Granger test. Build a z-score mean-reversion signal on the spread. Backtest with entry at ±2σ and exit at 0σ. Report Sharpe, max drawdown, and number of roundtrip trades
- **Momentum Strategy:** Rank all stocks monthly by 12-1 month momentum. Go long top decile, short bottom decile. Rebalance monthly. Compute the momentum premium and its drawdown during reversals (e.g. 2009 crash)
- **Smart Beta / Factor Investing:** Construct a multi-factor score (value: P/B + E/P, quality: ROE + low debt, momentum: 6-month return). Build a factor-weighted long-only portfolio. Compare risk-adjusted return vs equal-weight and market-cap-weight benchmarks
- **Machine Learning Alpha:** Train a Random Forest to predict whether a stock will beat the market next month using 10 features (momentum, value ratios, volatility, volume). Use walk-forward cross-validation (no lookahead). Report feature importances and strategy performance
- **Backtesting Pitfalls:** Intentionally introduce and then fix: (a) lookahead bias, (b) survivorship bias, (c) overfitting via too many parameters. Show quantitatively how each inflates backtest Sharpe by comparing biased vs clean results

**Topics Covered:** Stat arb · Cointegration · Momentum · Mean-reversion · Smart beta · Factor scoring · ML in finance · Backtesting bias detection

**✅ Deliverable:** Research platform with 3 strategy equity curves, factor attribution, ML feature importance chart, and a bias analysis report showing clean vs biased Sharpe ratios side by side.

---

### 🎯 Capstone Project · End-to-End Quant Investment System
**Month:** March 2027 · **Duration:** 3 weeks

**Goal:** Integrate all 10 modules into a single production-style quant system.

**Components:**

| Component | Module(s) Used |
|---|---|
| Company screening & valuation | M1 · M2 |
| Covariance matrix & PCA risk decomposition | M3 |
| Factor model & alpha estimation | M4 · M5 |
| Portfolio construction & rebalancing | M5 · M9 |
| Options overlay for downside hedging | M6 |
| VaR, CVaR, stress testing risk report | M7 |
| Bond allocation & yield curve positioning | M8 |
| Systematic signal & ML alpha layer | M10 |

**Tasks:**
- Screen a universe of 50 stocks using M2 financial ratios and M4 factor exposures
- Construct an optimal multi-asset portfolio (equities + bonds + gold) using M5 mean-variance with M3 PCA-based covariance
- Add a systematic momentum/mean-reversion signal from M10 as an alpha overlay
- Hedge tail risk using a put options strategy from M6 (protective put or collar)
- Generate a full risk report (M7): VaR, CVaR, factor risk decomposition, stress test
- Build and deploy a Streamlit dashboard with live data that shows portfolio holdings, performance, risk metrics, and signal status

**✅ Final Deliverable:**
- Live Streamlit app with real market data
- Full backtested strategy (2020–2026) with Pyfolio tear sheet
- 8-page quant research brief (methodology, results, risk analysis)
- Clean GitHub repo with documented code

---

## Month-by-Month Schedule

| Month | Module(s) | Mini Project |
|---|---|---|
| July 2026 | M1 · Finance Fundamentals | Company Valuation & Investment Calculator |
| August 2026 | M2 · Financial Accounting | Financial Health Screener (10 companies) |
| September 2026 | M3 · Quantitative Methods + M9 Python (start) | Quant Toolkit Notebook + Finance Dashboard |
| October 2026 | M4 · Investments & Asset Pricing + M9 Python (cont.) | Asset Pricing & Market Efficiency Analyser |
| November 2026 | M5 · Portfolio Theory | Portfolio Construction & Attribution Engine |
| December 2026 | M6 · Derivatives & Financial Engineering | Derivatives Pricing & Hedging Simulator |
| January 2027 | M7 · Risk Management | Enterprise Risk Dashboard |
| February 2027 | M8 · Fixed Income + M10 Quant Research (start) | Fixed Income Analytics Suite |
| March 2027 | M10 · Quant Research (cont.) + Capstone | Multi-Strategy Alpha Platform + Full Capstone |

---

## Bonus Topics (Optional / Post-March)

| Area | Book | Platform |
|---|---|---|
| ESG & Sustainable Finance | *Principles of Sustainable Finance* | edX – SDG Academy |
| Financial Econometrics | *Intro to Econometrics* – Stock & Watson | Coursera |
| FinTech | *The FINTECH Book* | University of Michigan |

---

## Practice & Interview Prep

| Resource | Type |
|---|---|
| *Heard on the Street* – Timothy Crack | Interview prep book |
| *Cases in Finance* – Bruner et al. | Case study book |
| QuantConnect | Strategy backtesting platform |
| Kaggle (Finance datasets) | Data practice |
| LeetCode / HackerRank | Quant coding challenges |

---

*Roadmap last updated: May 2026*