#!/usr/bin/env python3
"""
dashboard.py
─────────────────────────────────────────────────────────────
Stock Return PCA Decomposition  — Textual TUI Dashboard

Controls:
  r   → Re-run PCA (refresh data)
  q   → Quit
  Tab → Cycle tabs
"""

import sys
import os

# ── Inject vendored 'rich' from pip (available in this env) ──
_pip_vendor = "/usr/lib/python3/dist-packages/pip/_vendor"
if _pip_vendor not in sys.path:
    sys.path.insert(0, _pip_vendor)

import math
import json
import datetime
import numpy as np
import pandas as pd

# ── Rich imports (via vendored path) ─────────────────────
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.align import Align
from rich.rule import Rule
from rich.style import Style
from rich.live import Live
from rich import box
from rich.layout import Layout
from rich.padding import Padding

# ── Local modules ─────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from data_pipeline import Database, fetch_and_store, TICKERS, SECTOR_MAP, DB_PATH
from pca_engine import compute_pca, save_pca_run, portfolio_risk_decomposition


# ══════════════════════════════════════════════════════════
#  Visual helpers
# ══════════════════════════════════════════════════════════
PALETTE = {
    "pc1": "bright_cyan",
    "pc2": "bright_yellow",
    "pc3": "bright_magenta",
    "pos": "green",
    "neg": "red",
    "neutral": "white",
    "header": "bold bright_white on dark_blue",
    "title":  "bold bright_cyan",
    "accent": "bright_yellow",
    "dim":    "dim white",
    "border": "bright_blue",
}

PC_COLORS = [PALETTE["pc1"], PALETTE["pc2"], PALETTE["pc3"]]


def bar_chart(
    values: list[float],
    labels: list[str],
    width: int = 40,
    color: str = "bright_cyan",
    title: str = "",
    pct: bool = True,
) -> Table:
    """Render a horizontal bar chart as a Rich Table."""
    t = Table.grid(padding=(0, 1))
    t.add_column(justify="right",  style="dim white",  width=8)
    t.add_column(justify="left")
    t.add_column(justify="right", style="bright_white", width=7)

    max_val = max(abs(v) for v in values) if values else 1
    for lbl, val in zip(labels, values):
        filled = int(abs(val) / max_val * width)
        bar    = "█" * filled + "░" * (width - filled)
        clr    = color if val >= 0 else "red"
        suffix = f"{val*100:.1f}%" if pct else f"{val:.4f}"
        t.add_row(
            Text(lbl, style="white"),
            Text(bar, style=clr),
            Text(suffix, style="bright_white"),
        )
    if title:
        return Panel(t, title=f"[bold]{title}[/bold]",
                     border_style=PALETTE["border"])
    return t


def scree_chart(eigenvalues: np.ndarray, n_show: int = 10) -> Table:
    """Scree plot as a Rich bar chart."""
    vals   = eigenvalues[:n_show]
    total  = eigenvalues.sum()
    labels = [f"PC{i+1:02d}" for i in range(len(vals))]
    fracs  = (vals / total).tolist()

    t = Table.grid(padding=(0, 1))
    t.add_column(justify="right",  style="dim",   width=5)
    t.add_column(justify="left",   width=36)
    t.add_column(justify="right",  style="bright_white", width=7)
    t.add_column(justify="right",  style="dim", width=9)

    cumul = 0.0
    for i, (lbl, frac) in enumerate(zip(labels, fracs)):
        cumul  += frac
        filled  = int(frac * 36 / fracs[0])  # scale to first PC
        clr     = PC_COLORS[i] if i < 3 else "grey50"
        t.add_row(
            Text(lbl, style=clr),
            Text("█" * filled, style=clr),
            Text(f"{frac*100:.1f}%", style=clr),
            Text(f"Σ {cumul*100:.1f}%", style="dim"),
        )
    return Panel(t, title="[bold]Scree Plot — Explained Variance per PC[/bold]",
                 border_style=PALETTE["border"])


def loading_table(result, k: int, n_top: int = 10) -> Panel:
    """Top-N loadings for component k as a table."""
    vecs   = result.eigenvectors[:, k]
    signed = [(result.tickers[i], float(vecs[i])) for i in range(len(result.tickers))]
    signed.sort(key=lambda x: abs(x[1]), reverse=True)

    t = Table(show_header=True, header_style="bold",
              box=box.SIMPLE_HEAVY, expand=True)
    t.add_column("Ticker", style="bright_white", width=8)
    t.add_column("Sector", style="dim", width=12)
    t.add_column("Loading", justify="right", width=10)
    t.add_column("Bar", width=22)

    max_abs = max(abs(x[1]) for x in signed)
    for ticker, val in signed[:n_top]:
        clr    = PALETTE["pos"] if val >= 0 else PALETTE["neg"]
        filled = int(abs(val) / max_abs * 20)
        bar    = ("▶" if val >= 0 else "◀") + "█" * filled
        t.add_row(
            ticker,
            SECTOR_MAP.get(ticker, "—"),
            Text(f"{val:+.4f}", style=clr),
            Text(bar, style=clr),
        )

    color = PC_COLORS[k] if k < 3 else "white"
    label = result.component_labels[k] if k < len(result.component_labels) else f"PC{k+1}"
    return Panel(t, title=f"[bold {color}]{label}[/bold {color}]",
                 border_style=color)


def covariance_heatmap(cov: np.ndarray, tickers: list[str], title="") -> Panel:
    """ASCII heatmap of correlation matrix (derived from cov)."""
    std  = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)
    corr = np.clip(corr, -1, 1)

    BLOCKS = " ░▒▓█"

    t = Table.grid()
    # header row
    header = Text("     ")
    for tk in tickers:
        header.append(f"{tk[:4]:>5}", style="dim")
    t.add_row(header)

    for i, row_tk in enumerate(tickers):
        row_text = Text(f"{row_tk[:4]:>4} ")
        for j in range(len(tickers)):
            v     = corr[i, j]
            level = int((v + 1) / 2 * (len(BLOCKS) - 1))
            level = max(0, min(level, len(BLOCKS) - 1))
            if i == j:
                row_text.append(BLOCKS[level] * 2 + "   ", style="bright_white")
            elif v > 0.5:
                row_text.append(BLOCKS[level] * 2 + "   ", style="green")
            elif v < -0.2:
                row_text.append(BLOCKS[level] * 2 + "   ", style="red")
            else:
                row_text.append(BLOCKS[level] * 2 + "   ", style="yellow")
        t.add_row(row_text)

    return Panel(t, title=f"[bold]{title or 'Correlation Heatmap'}[/bold]",
                 border_style=PALETTE["border"])


def risk_decomp_table(risk: dict, result) -> Panel:
    """Portfolio risk decomposition table."""
    t = Table(show_header=True, header_style="bold",
              box=box.SIMPLE_HEAVY, expand=True)
    t.add_column("Factor",     style="bright_white",  width=30)
    t.add_column("Ann. Vol %", justify="right", width=12)
    t.add_column("% of Total", justify="right", width=12)
    t.add_column("Bar",        width=24)

    total_vol = risk["total_vol_ann"]

    def vol_bar(pct, color):
        filled = int(pct / 100 * 22)
        return Text("█" * filled + "░" * (22 - filled), style=color)

    t.add_row(
        "[bold bright_white]Total Portfolio[/bold bright_white]",
        f"{total_vol:.2f}%",
        "100.00%",
        vol_bar(100, "bright_white"),
    )
    t.add_row("", "", "", "")  # spacer

    for k, (vol, pct) in enumerate(
        zip(risk["component_vols"], risk["pct_explained"])
    ):
        lbl   = result.component_labels[k] if k < len(result.component_labels) else f"PC{k+1}"
        color = PC_COLORS[k]
        t.add_row(
            Text(lbl, style=color),
            Text(f"{vol:.2f}%", style=color),
            Text(f"{pct:.1f}%",  style=color),
            vol_bar(pct, color),
        )

    t.add_row(
        Text("Residual / Idiosyncratic", style="dim"),
        Text(f"{np.sqrt(risk['residual_var']*252)*100:.2f}%", style="dim"),
        Text(f"{risk['pct_residual']:.1f}%", style="dim"),
        vol_bar(risk["pct_residual"], "grey50"),
    )

    return Panel(t,
                 title="[bold]Equal-Weight Portfolio Risk Decomposition[/bold]",
                 border_style=PALETTE["border"])


# ══════════════════════════════════════════════════════════
#  Dashboard renderer
# ══════════════════════════════════════════════════════════
def render_dashboard(console: Console, result, risk: dict, source: str,
                     run_id: int | None = None):
    """Print the full TUI dashboard to console."""
    console.clear()

    # ── Banner ─────────────────────────────────────────────
    banner = Text()
    banner.append("  ██████╗  ██████╗ █████╗ ", style="bright_cyan")
    banner.append("Stock Return PCA Decomposition\n", style="bold bright_white")
    banner.append("  ██╔══██╗██╔════╝██╔══██╗", style="bright_cyan")
    banner.append(f" {len(result.tickers)} stocks · "
                  f"{len(result.returns)} days · "
                  f"Top-{result.n_components} PCs\n", style="dim")
    banner.append("  ███████║██║     ███████║", style="bright_cyan")
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    banner.append(f" Source: {source:<14} Run #{run_id}  {ts}\n", style="dim")
    console.print(Panel(banner, border_style="bright_cyan", padding=(0, 1)))

    # ── Row 1: Scree + Risk decomp ─────────────────────────
    console.print(Columns([
        scree_chart(result.eigenvalues, n_show=min(10, len(result.tickers))),
        risk_decomp_table(risk, result),
    ], equal=True, expand=True))

    # ── Row 2: Component loadings ──────────────────────────
    console.print(Rule("[bold bright_cyan]Top-3 Principal Component Loadings[/bold bright_cyan]",
                        style="bright_cyan"))
    console.print(Columns([
        loading_table(result, 0),
        loading_table(result, 1),
        loading_table(result, 2),
    ], equal=True, expand=True))

    # ── Row 3: Cumulative explained variance ───────────────
    n_show = min(15, len(result.tickers))
    cum_labels = [f"PC{i+1}" for i in range(n_show)]
    cum_vals   = result.cumulative_var[:n_show].tolist()
    console.print(bar_chart(
        cum_vals, cum_labels, width=50,
        color="bright_green",
        title="Cumulative Explained Variance (PCA scree, top-15 PCs)",
        pct=True,
    ))

    # ── Row 4: Per-PC annualised vol contribution ──────────
    factor_vols = risk["component_vols"][:3]
    factor_lbls = [f"PC{k+1}" for k in range(3)]
    factor_vals = [v / risk["total_vol_ann"] for v in factor_vols]
    console.print(bar_chart(
        factor_vals, factor_lbls, width=40,
        color="bright_yellow",
        title="Factor Vol as % of Total Annualised Volatility",
        pct=True,
    ))

    # ── Row 5: Correlation heatmap (compact) ──────────────
    n_heat = min(12, len(result.tickers))
    sub_tk = result.tickers[:n_heat]
    idx    = [result.tickers.index(t) for t in sub_tk]
    sub_cov = result.cov_matrix[np.ix_(idx, idx)]
    console.print(covariance_heatmap(sub_cov, sub_tk,
                  title="Asset Correlation Heatmap (first 12 stocks)"))

    # ── Footer ─────────────────────────────────────────────
    console.print(Rule(style="bright_blue"))
    console.print(
        Align(
            Text(
                "  [r] Re-run  [q] Quit  "
                "Eigenvalue decomp: numpy.linalg.eigh  "
                f"DB: {DB_PATH}  ",
                style="dim",
            ),
            align="center",
        )
    )


# ══════════════════════════════════════════════════════════
#  Main interactive loop
# ══════════════════════════════════════════════════════════
def run_dashboard():
    console = Console(force_terminal=True, color_system="truecolor")
    db      = Database(DB_PATH)

    def do_run(force: bool = False):
        console.clear()
        with console.status("[bright_cyan]Fetching price data…[/bright_cyan]"):
            price_df, source = fetch_and_store(db, force_refresh=force)

        with console.status("[bright_cyan]Running PCA decomposition…[/bright_cyan]"):
            result = compute_pca(price_df, n_components=3)
            run_id = save_pca_run(db, result)
            risk   = portfolio_risk_decomposition(result)

        render_dashboard(console, result, risk, source, run_id)
        return result, risk

    result, risk = do_run()

    # Interactive key-loop (fallback to single-render if not tty)
    if not sys.stdin.isatty():
        return

    import termios, tty

    def getch():
        fd   = sys.stdin.fileno()
        old  = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    console.print("\n[dim]Press [bold]r[/bold] to refresh · "
                  "[bold]q[/bold] to quit[/dim]")

    while True:
        try:
            ch = getch()
        except Exception:
            break
        if ch.lower() == "q":
            console.print("\n[bright_cyan]Goodbye![/bright_cyan]")
            break
        elif ch.lower() == "r":
            result, risk = do_run(force=True)
            console.print("\n[dim]Press [bold]r[/bold] to refresh · "
                          "[bold]q[/bold] to quit[/dim]")


if __name__ == "__main__":
    run_dashboard()
