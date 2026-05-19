# Math for Quantitative Finance & AI/ML
### July 2026 – May 2027 · 11 Months · 20 Topics + 20 Finance Projects

> Each topic is paired with a hands-on finance project so you learn the math
> *through* real financial problems — not in isolation.

---

## Overview

| Detail | Info |
|---|---|
| **Duration** | July 2026 – May 2027 (11 months) |
| **Total Topics** | 20 Math Topics |
| **Projects** | 20 Finance Projects (1 per topic) |
| **Goal** | Build quant-ready math skills through applied finance problems |

---

## Schedule at a Glance

| Month | Topics |
|---|---|
| July 2026 | T1 · Linear Algebra, T2 · Probability & Statistics |
| August 2026 | T3 · Stochastic Processes, T4 · Regression Analysis |
| September 2026 | T5 · Value at Risk Models, T6 · Time Series Analysis |
| October 2026 | T7 · Volatility Modeling, T8 · Regularized Pricing & Risk Models |
| November 2026 | T9 · Commodity Models, T10 · Portfolio Theory |
| December 2026 | T11 · Factor Modeling, T12 · Portfolio Management |
| January 2027 | T13 · Itō Calculus, T14 · Black-Scholes & Risk-Neutral Valuation |
| February 2027 | T15 · Option Price & Probability Duality, T16 · Stochastic Differential Equations |
| March 2027 | T17 · Quanto Credit Hedging, T18 · HJM Model for Interest Rates |
| April 2027 | T19 · Ross Recovery Theorem, T20 · Counterparty Credit Risk |
| May 2027 | Capstone Integration Month |

---

## July 2026

---

### T1 · Linear Algebra
**Duration:** 2 weeks

**Subtopics:**
- Vectors, vector spaces, and inner product spaces
- Matrices and matrix operations
- Eigenvalues and eigenvectors
- Diagonalization and SVD (Singular Value Decomposition)
- Matrix calculus and Jacobians
- Applications in ML: PCA, least squares

**🎯 Finance Project: Stock Return PCA Decomposition**
Use daily returns of 20 Nifty 50 / S&P 500 stocks. Build a covariance matrix, run PCA using eigenvalue decomposition, and identify the top 3 principal components. Interpret them as market, sector, and idiosyncratic risk factors. Visualise explained variance and reconstruct the portfolio risk using only the top components.

**✅ Deliverable:** Python notebook — PCA on stock returns with explained variance plot and factor interpretation.

---

### T2 · Probability & Statistics
**Duration:** 2 weeks

**Subtopics:**
- Combinatorics and Bayes' Theorem
- Random variables, PDFs, CDFs
- Expectation, Variance, Covariance
- Common distributions (Normal, Poisson, Binomial)
- Law of Large Numbers and Central Limit Theorem
- Statistical inference: Estimation and Hypothesis testing

**🎯 Finance Project: Return Distribution Analyser**
Pull 5 years of daily returns for 5 stocks. Fit Normal and Student-t distributions to each. Test normality using Jarque-Bera and Shapiro-Wilk tests. Visualise the fat tails and compute excess kurtosis. Use Bayes' theorem to estimate the probability that a return exceeds a threshold given yesterday's market move.

**✅ Deliverable:** Report comparing distribution fits across stocks with annotated fat-tail plots.

---

## August 2026

---

### T3 · Stochastic Processes
**Duration:** 2 weeks

**Subtopics:**
- Markov chains (discrete and continuous)
- Brownian motion (Wiener process)
- Poisson process
- Martingales
- Stationarity and ergodicity

**🎯 Finance Project: Market Regime Simulator**
Model bull/bear/sideways market regimes as a 3-state discrete Markov chain. Estimate the transition matrix from historical monthly returns (S&P 500). Simulate 1,000 regime paths over 12 months. Compute the stationary distribution and the expected time spent in each regime. Overlay simulated paths with actual 2020–2024 regime history.

**✅ Deliverable:** Markov chain model with transition heatmap and 1,000-path Monte Carlo regime simulation.

---

### T4 · Regression Analysis
**Duration:** 2 weeks

**Subtopics:**
- Simple and multiple linear regression
- Assumptions and diagnostics
- Maximum Likelihood Estimation (MLE)
- Logistic regression
- Multicollinearity and heteroskedasticity
- Residual analysis

**🎯 Finance Project: Stock Return Factor Regression**
Regress a stock's monthly returns on Fama-French 3 factors (market, size, value). Use OLS and MLE. Run full regression diagnostics — check for heteroskedasticity (Breusch-Pagan), autocorrelation (Durbin-Watson), and multicollinearity (VIF). Then build a logistic regression model to classify whether a stock beats the benchmark in a given month.

**✅ Deliverable:** Regression report with diagnostic plots and a classification accuracy score for the logistic model.

---

## September 2026

---

### T5 · Value at Risk (VaR) Models
**Duration:** 2 weeks

**Subtopics:**
- Historical simulation
- Parametric (variance-covariance) approach
- Monte Carlo simulation
- Conditional VaR (CVaR / Expected Shortfall)
- VaR in portfolios

**🎯 Finance Project: Portfolio Risk Dashboard**
Build a 5-asset portfolio (mix of equities, bonds, and commodities). Compute 1-day and 10-day VaR at 95% and 99% confidence using all three methods. Compare them side by side. Add CVaR for the tail beyond VaR. Backtest historical VaR using a rolling 252-day window and report VaR breaches.

**✅ Deliverable:** Interactive Streamlit dashboard showing VaR, CVaR, and backtesting breach count.

---

### T6 · Time Series Analysis
**Duration:** 2 weeks

**Subtopics:**
- AR, MA, ARMA, ARIMA models
- Seasonality and stationarity
- ACF and PACF plots
- GARCH models (overview)
- Forecasting and model selection (AIC/BIC)

**🎯 Finance Project: Stock Price Forecaster**
Select a stock index (e.g. Nifty 50). Test for stationarity using ADF and KPSS tests. Identify AR/MA orders using ACF and PACF. Fit ARIMA and compare AIC/BIC across model orders. Produce a 30-day return forecast with confidence intervals. Evaluate out-of-sample RMSE and MAPE against a naive baseline.

**✅ Deliverable:** ARIMA forecasting notebook with model selection table and 30-day forecast plot.

---

## October 2026

---

### T7 · Volatility Modeling
**Duration:** 2 weeks

**Subtopics:**
- ARCH, GARCH, EGARCH models
- Stochastic volatility models
- Volatility clustering
- Volatility smile and skew
- Realized vs implied volatility

**🎯 Finance Project: Volatility Surface Builder**
Fit a GARCH(1,1) model to daily returns of a stock index. Plot the conditional volatility over time and highlight volatility clustering. Scrape or download options data and compute implied volatility across strikes and maturities. Plot the volatility smile and surface. Compare GARCH-forecasted volatility with realised and implied volatility.

**✅ Deliverable:** Volatility clustering plot + implied volatility surface visualisation.

---

### T8 · Regularized Pricing & Risk Models
**Duration:** 2 weeks

**Subtopics:**
- Ridge and Lasso regression
- Elastic Net
- Model complexity and overfitting
- Bias-variance tradeoff
- Applications to pricing models

**🎯 Finance Project: Options Pricing with Regularized Regression**
Use a dataset of historical option prices (or simulate with BSM). Engineer features: moneyness, time to expiry, implied volatility, delta. Train Ridge, Lasso, and Elastic Net models to predict option prices. Use cross-validation to tune lambda. Compare prediction error and discuss which features Lasso zeroes out and why.

**✅ Deliverable:** Regularization path plots + model comparison table (RMSE, R², feature importance).

---

## November 2026

---

### T9 · Commodity Models
**Duration:** 2 weeks

**Subtopics:**
- Spot and forward price modeling
- Convenience yield
- Mean-reverting models (Ornstein-Uhlenbeck)
- Seasonality in commodities
- Storage models

**🎯 Finance Project: Crude Oil Mean-Reversion Trader**
Download WTI crude oil daily prices (2015–2024). Fit an Ornstein-Uhlenbeck model to the log-price series — estimate speed of mean-reversion (κ), long-run mean (μ), and volatility (σ). Simulate forward price paths. Build a simple pairs-trading signal: go long when price is 1.5σ below mean, short when 1.5σ above. Backtest the strategy and report Sharpe ratio.

**✅ Deliverable:** OU parameter estimates + backtest equity curve with performance metrics.

---

### T10 · Portfolio Theory
**Duration:** 2 weeks

**Subtopics:**
- Markowitz mean-variance model
- Efficient frontier
- CAPM (Capital Asset Pricing Model)
- Risk-return tradeoff
- Diversification and correlation

**🎯 Finance Project: Efficient Frontier Builder**
Select 10 assets across asset classes (equities, bonds, gold, REITs). Compute expected returns and covariance matrix from historical data. Run mean-variance optimization using CVXPY with short-selling constraints. Plot the efficient frontier and highlight the minimum-variance and maximum-Sharpe portfolios. Add the Capital Market Line using the risk-free rate.

**✅ Deliverable:** Interactive efficient frontier plot with portfolio weights table for key points.

---

## December 2026

---

### T11 · Factor Modeling
**Duration:** 2 weeks

**Subtopics:**
- Single- and multi-factor models
- Fama-French 3/5-factor model
- Macro and statistical factors
- Factor risk premia
- APT (Arbitrage Pricing Theory)

**🎯 Finance Project: Multi-Factor Alpha Model**
Download Fama-French 5-factor data. Regress a portfolio of 10 Indian/US stocks on all 5 factors. Compute factor exposures (betas) and isolate the alpha (intercept). Then build your own macro factor (e.g. INR/USD rate, oil price) and add it as a 6th factor. Test whether it improves adjusted R² and reduces unexplained alpha.

**✅ Deliverable:** Factor exposure heatmap + alpha table before and after adding the custom macro factor.

---

### T12 · Portfolio Management
**Duration:** 2 weeks

**Subtopics:**
- Asset allocation strategies
- Performance evaluation (Sharpe, Sortino, Calmar ratios)
- Rebalancing strategies (threshold vs calendar)
- Risk budgeting
- Strategic vs tactical allocation

**🎯 Finance Project: Rebalancing Strategy Comparator**
Build a 60/40 equity-bond portfolio. Implement and backtest three rebalancing strategies: monthly calendar, 5% threshold drift, and risk parity (equal risk contribution). Compute Sharpe, Sortino, Calmar, and max drawdown for each. Analyse how transaction costs affect net performance and identify the most efficient rebalancing approach.

**✅ Deliverable:** Side-by-side equity curves + performance metrics table for all three strategies.

---

## January 2027

---

### T13 · Itō Calculus
**Duration:** 2 weeks

**Subtopics:**
- Itō's lemma
- Stochastic integrals
- Application to Brownian motion
- Chain rule in stochastic calculus

**🎯 Finance Project: GBM Stock Price Simulator**
Use Itō's lemma to derive the closed-form solution for Geometric Brownian Motion (GBM). Calibrate drift (μ) and volatility (σ) from historical stock data. Simulate 10,000 price paths over 252 trading days. Compute the distribution of terminal prices and compare the simulated mean and variance with the theoretical values derived from Itō's lemma.

**✅ Deliverable:** 10,000-path GBM simulation with terminal price histogram vs theoretical log-normal overlay.

---

### T14 · Black-Scholes Formula & Risk-Neutral Valuation
**Duration:** 2 weeks

**Subtopics:**
- Derivation using Itō calculus
- Greeks (Delta, Gamma, Vega, Theta, Rho)
- Change of measure (Girsanov's theorem)
- Martingale representation
- Risk-neutral pricing logic

**🎯 Finance Project: Options Greeks Dashboard**
Implement the full Black-Scholes model from scratch (no libraries). Price European call and put options across a grid of strikes and maturities. Compute all five Greeks analytically. Build an interactive Streamlit app where the user adjusts S, K, T, r, σ and sees the option price and Greeks update in real time. Add a P&L heatmap for a delta-hedged position.

**✅ Deliverable:** Streamlit BSM dashboard with live Greeks and delta-hedge P&L heatmap.

---

## February 2027

---

### T15 · Option Price & Probability Duality
**Duration:** 2 weeks

**Subtopics:**
- Expected payoff interpretation
- Implied probabilities from option prices
- Martingale vs physical measures
- Payoff functions and replication

**🎯 Finance Project: Risk-Neutral Probability Extractor**
Use a chain of call option prices at different strikes (same maturity) to extract the risk-neutral probability density function (PDF) using the Breeden-Litzenberger formula. Plot the implied PDF and compare it with the historical return distribution of the underlying. Quantify the difference in tail probabilities and discuss what the market is pricing in.

**✅ Deliverable:** Risk-neutral PDF plot vs historical PDF with annotated tail probability comparison.

---

### T16 · Stochastic Differential Equations (SDEs)
**Duration:** 2 weeks

**Subtopics:**
- Solving SDEs analytically and numerically
- Fokker-Planck and Kolmogorov equations
- Euler-Maruyama numerical scheme
- Connection with option pricing models

**🎯 Finance Project: Interest Rate Path Simulator**
Implement and simulate three interest rate SDEs: Vasicek, Cox-Ingersoll-Ross (CIR), and Hull-White models using Euler-Maruyama. Calibrate each to current yield curve data. Compare simulated short-rate distributions and zero-coupon bond prices. Analyse mean-reversion behaviour and volatility structure across models.

**✅ Deliverable:** Side-by-side simulated rate paths for all three models + calibrated zero-coupon bond price curves.

---

## March 2027

---

### T17 · Quanto Credit Hedging
**Duration:** 2 weeks

**Subtopics:**
- FX and interest rate hybrid models
- Credit risk in foreign currency
- Credit Valuation Adjustment (CVA)
- Hedging with options and swaps

**🎯 Finance Project: CVA Calculator for a Cross-Currency Swap**
Simulate a 5-year USD/INR cross-currency swap between two counterparties. Model the FX rate as GBM and the counterparty's default intensity as a Poisson process. Compute unilateral CVA as the discounted expected loss given default (using Monte Carlo). Show how CVA changes with correlation between FX rates and default intensity (wrong-way risk).

**✅ Deliverable:** CVA vs wrong-way risk correlation plot + Monte Carlo simulation with confidence intervals.

---

### T18 · HJM Model for Interest Rates & Credit
**Duration:** 2 weeks

**Subtopics:**
- Forward rate modeling
- No-arbitrage drift restriction (HJM drift condition)
- Model implementation and calibration
- Application to credit spread modeling

**🎯 Finance Project: Yield Curve Evolution Model**
Implement a simplified 1-factor HJM model. Use bootstrapped forward rates from Indian or US government bond yields as the initial forward curve. Simulate the evolution of the entire yield curve over 1 year using the HJM drift restriction. Price a 2-year zero-coupon bond and a 5-year bond under the model and compare with market prices.

**✅ Deliverable:** Animated yield curve evolution + bond pricing error table vs market prices.

---

## April 2027

---

### T19 · Ross Recovery Theorem
**Duration:** 2 weeks

**Subtopics:**
- Recovering physical probability from option prices
- Assumptions and limitations of the theorem
- Applications in market recovery
- Connection with risk-neutral valuation

**🎯 Finance Project: Physical vs Risk-Neutral Probability Comparison**
Apply the Ross Recovery theorem to S&P 500 option prices. Extract the transition probability matrix from the pricing kernel implied by options data. Recover the physical (real-world) probability distribution and compare it with the risk-neutral distribution and the historical empirical distribution. Discuss where the three distributions diverge and what this implies for expected returns.

**✅ Deliverable:** Three-way probability distribution comparison plot with interpretation of market implied expectations.

---

### T20 · Introduction to Counterparty Credit Risk
**Duration:** 2 weeks

**Subtopics:**
- Credit Exposure (PFE, EPE, EE)
- CVA and DVA
- Wrong-way risk
- Netting and collateral agreements
- Basel III guidelines on CCR

**🎯 Finance Project: Counterparty Exposure Profile for an Interest Rate Swap**
Simulate a 10-year interest rate swap (pay fixed, receive floating). Use Monte Carlo with a Vasicek interest rate model to generate 5,000 rate paths. At each monthly time step, compute the mark-to-market value and derive the Expected Exposure (EE) and Potential Future Exposure (PFE) at 95%. Add a netting agreement and collateral threshold and show how they reduce exposure.

**✅ Deliverable:** EE and PFE exposure profile chart + netting/collateral impact comparison.

---

## May 2027 · Capstone Integration Month

> *Bring everything together into one end-to-end quantitative research project.*

---

### 🎯 Capstone: Full-Stack Quant Risk & Strategy System

**Duration:** 4 weeks

**Goal:** Build a production-style quant system that integrates math from all 20 topics.

**Components:**

| Component | Math Used |
|---|---|
| Asset universe selection (10 assets) | PCA (T1), Factor Models (T11) |
| Return distribution analysis | Probability (T2), Time Series (T6) |
| Volatility forecasting | GARCH / Volatility Modeling (T7) |
| Portfolio construction | Portfolio Theory (T10), Management (T12) |
| Options overlay for hedging | BSM (T14), Greeks, SDEs (T16) |
| Risk reporting (VaR, CVaR, PFE) | VaR Models (T5), CCR (T20) |
| Strategy backtesting | Regression (T4), Regularization (T8) |
| Research brief | Ross Recovery (T19), Factor Premia (T11) |

**✅ Final Deliverable:**
- A Streamlit or Dash web app with live data feeds
- Full backtested strategy with risk decomposition
- 10-page quant research paper
- GitHub repository with clean, documented code

---

## Tools & Libraries Reference

| Tool | Use |
|---|---|
| `numpy`, `scipy` | Linear algebra, distributions, optimization |
| `pandas` | Time series, data wrangling |
| `statsmodels` | Regression, ARIMA, hypothesis testing |
| `arch` | GARCH and volatility models |
| `cvxpy` | Portfolio optimization |
| `yfinance`, `pandas-datareader` | Market data |
| `matplotlib`, `seaborn`, `plotly` | Visualisation |
| `streamlit` | Interactive dashboards |
| `QuantLib` (optional) | Derivatives pricing, yield curves |

---

## Recommended Books by Topic

| Topic | Book |
|---|---|
| Linear Algebra | *Linear Algebra Done Right* – Axler |
| Probability & Statistics | *Introduction to Probability* – Blitzstein & Hwang |
| Stochastic Processes | *Introduction to Stochastic Processes* – Lawler |
| Regression | *The Elements of Statistical Learning* – Hastie, Tibshirani |
| VaR & Risk | *Value at Risk* – Philippe Jorion |
| Time Series | *Time Series Analysis* – Hamilton |
| Volatility | *The Volatility Surface* – Jim Gatheral |
| Portfolio Theory | *Quantitative Investment Analysis* – CFA Institute |
| Itō Calculus & SDEs | *Stochastic Calculus for Finance II* – Shreve |
| Black-Scholes | *Options, Futures & Other Derivatives* – John C. Hull |
| Factor Models | *Active Portfolio Management* – Grinold & Kahn |
| Counterparty Risk | *Counterparty Credit Risk* – Jon Gregory |
| HJM / Interest Rates | *Interest Rate Models* – Brigo & Mercurio |

---

*Roadmap last updated: May 2026*