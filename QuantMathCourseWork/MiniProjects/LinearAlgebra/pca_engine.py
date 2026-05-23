"""
pca_engine.py
─────────────────────────────────────────────────────────────
Core PCA decomposition via eigenvalue decomposition of the
sample covariance matrix.

Components are interpreted as:
  PC1 → Market risk   (high positive loadings across all stocks)
  PC2 → Sector risk   (opposing loadings across sector groups)
  PC3 → Idiosyncratic (mixed/residual variance)
"""

import json
import datetime
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PCAResult:
    """Complete PCA decomposition result."""
    # Inputs
    tickers:        list[str]
    returns:        pd.DataFrame          # (T × N) daily returns
    cov_matrix:     np.ndarray            # (N × N)

    # Eigendecomposition
    eigenvalues:    np.ndarray            # sorted descending
    eigenvectors:   np.ndarray            # columns = PCs (N × N)

    # Derived
    explained_var:  np.ndarray            # fraction explained per PC
    cumulative_var: np.ndarray

    # Loadings (N × k top components)
    loadings:       np.ndarray
    n_components:   int

    # Reconstruction
    recon_cov:      np.ndarray            # reconstructed from top-k PCs
    recon_returns:  pd.DataFrame          # projected returns

    # Labels
    component_labels: list[str] = field(default_factory=list)
    run_id:           Optional[int] = None


def compute_pca(
    price_df: pd.DataFrame,
    n_components: int = 3,
) -> PCAResult:
    """
    Full PCA pipeline:

    1. Compute log daily returns
    2. Standardise (zero-mean)
    3. Build sample covariance matrix (unbiased, 1/T-1)
    4. Eigenvalue decomposition via numpy.linalg.eigh
       (symmetric matrix → guaranteed real eigenvalues)
    5. Sort by descending eigenvalue
    6. Extract loadings (eigenvectors scaled by √eigenvalue)
    7. Reconstruct covariance from top-k PCs
    8. Project returns into PC space

    Returns PCAResult dataclass.
    """
    # ── 1. Log returns ────────────────────────────────────
    log_ret = np.log(price_df / price_df.shift(1)).dropna()
    tickers = list(log_ret.columns)
    T, N    = log_ret.shape

    R = log_ret.values  # (T × N)

    # ── 2. Demean ─────────────────────────────────────────
    R_c = R - R.mean(axis=0)

    # ── 3. Covariance matrix ──────────────────────────────
    Σ = (R_c.T @ R_c) / (T - 1)          # (N × N)

    # ── 4. Eigendecomposition ─────────────────────────────
    #  np.linalg.eigh returns eigenvalues in ascending order
    raw_vals, raw_vecs = np.linalg.eigh(Σ)

    # ── 5. Sort descending ────────────────────────────────
    idx       = np.argsort(raw_vals)[::-1]
    eigvals   = raw_vals[idx]
    eigvecs   = raw_vecs[:, idx]          # (N × N) columns = PCs

    total_var      = eigvals.sum()
    explained_var  = eigvals / total_var
    cumulative_var = np.cumsum(explained_var)

    # ── 6. Loadings ───────────────────────────────────────
    # Loading = eigenvector_i * sqrt(eigenvalue_i)
    # Represents the "contribution" of each stock to each PC
    loadings = eigvecs[:, :n_components] * np.sqrt(eigvals[:n_components])

    # ── 7. Reconstruct covariance from top-k ─────────────
    recon_cov = (
        eigvecs[:, :n_components]
        @ np.diag(eigvals[:n_components])
        @ eigvecs[:, :n_components].T
    )

    # ── 8. Project returns into PC space ──────────────────
    scores = R_c @ eigvecs[:, :n_components]   # (T × k)
    recon_ret_vals = scores @ eigvecs[:, :n_components].T  # (T × N)
    recon_returns = pd.DataFrame(
        recon_ret_vals,
        index=log_ret.index,
        columns=tickers,
    )

    # ── 9. Auto-label components ──────────────────────────
    component_labels = _label_components(eigvecs, tickers, n_components)

    return PCAResult(
        tickers=tickers,
        returns=log_ret,
        cov_matrix=Σ,
        eigenvalues=eigvals,
        eigenvectors=eigvecs,
        explained_var=explained_var,
        cumulative_var=cumulative_var,
        loadings=loadings,
        n_components=n_components,
        recon_cov=recon_cov,
        recon_returns=recon_returns,
        component_labels=component_labels,
    )


def _label_components(
    eigvecs: np.ndarray,
    tickers: list[str],
    n_components: int,
) -> list[str]:
    """
    Heuristic labelling:
    PC1: if all loadings have same sign → 'Market / Systematic'
    PC2: if loadings split into two groups → 'Sector / Style'
    PC3+: 'Idiosyncratic / Residual'
    """
    labels = []
    for k in range(n_components):
        v = eigvecs[:, k]
        pos = (v > 0).sum()
        neg = (v < 0).sum()
        if pos == 0 or neg == 0:
            labels.append(f"PC{k+1} — Market / Systematic")
        elif abs(pos - neg) < len(tickers) * 0.25:
            labels.append(f"PC{k+1} — Sector / Style")
        elif k == 0:
            labels.append(f"PC{k+1} — Market / Systematic")
        elif k == 1:
            labels.append(f"PC{k+1} — Sector / Style")
        else:
            labels.append(f"PC{k+1} — Idiosyncratic / Residual")
    return labels


def save_pca_run(db, result: PCAResult) -> int:
    """Persist PCA run metadata to the database."""
    cur = db.execute(
        """INSERT INTO pca_runs
           (run_at, n_stocks, n_components, lookback_days,
            explained_var, eigenvalues, loadings)
           VALUES (?,?,?,?,?,?,?)""",
        (
            datetime.datetime.utcnow().isoformat(),
            len(result.tickers),
            result.n_components,
            len(result.returns),
            json.dumps(result.explained_var[:result.n_components].tolist()),
            json.dumps(result.eigenvalues[:result.n_components].tolist()),
            json.dumps(result.loadings.tolist()),
        ),
    )
    run_id = cur.lastrowid
    db.commit()

    # Store per-component loadings
    rows = []
    for k in range(result.n_components):
        for i, ticker in enumerate(result.tickers):
            rows.append((run_id, k + 1, ticker, float(result.loadings[i, k])))
    db.executemany(
        "INSERT INTO pca_components (run_id, component, ticker, loading) "
        "VALUES (?,?,?,?)",
        rows,
    )
    db.commit()
    result.run_id = run_id
    return run_id


# ── Risk metrics ──────────────────────────────────────────
def portfolio_risk_decomposition(
    result: PCAResult,
    weights: Optional[np.ndarray] = None,
) -> dict:
    """
    Compute total and component-wise portfolio variance.

    weights: equal-weight if None
    Returns dict with total_var, component_vars, residual_var,
    annualised_vol, component_vols.
    """
    N = len(result.tickers)
    if weights is None:
        weights = np.ones(N) / N

    total_var      = float(weights @ result.cov_matrix @ weights)
    recon_var      = float(weights @ result.recon_cov   @ weights)
    residual_var   = total_var - recon_var

    # Per-component variance
    component_vars = []
    for k in range(result.n_components):
        cov_k = (
            result.eigenvectors[:, k:k+1]
            @ np.diag([result.eigenvalues[k]])
            @ result.eigenvectors[:, k:k+1].T
        )
        component_vars.append(float(weights @ cov_k @ weights))

    return {
        "total_var":      total_var,
        "total_vol_ann":  np.sqrt(total_var * 252) * 100,
        "recon_var":      recon_var,
        "residual_var":   residual_var,
        "component_vars": component_vars,
        "component_vols": [np.sqrt(v * 252) * 100 for v in component_vars],
        "pct_explained":  [v / total_var * 100 for v in component_vars],
        "pct_residual":   residual_var / total_var * 100,
    }
