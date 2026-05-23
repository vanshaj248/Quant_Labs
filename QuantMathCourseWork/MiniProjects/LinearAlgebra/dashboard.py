#!/usr/bin/env python3
"""
dashboard.py  ·  Stock Return PCA Decomposition  ·  Rich TUI
─────────────────────────────────────────────────────────────
Keys:  1/2/3 → switch tabs   r → refresh   q → quit
"""

import sys, os, datetime, math
import numpy as np

_pip_vendor = "/usr/lib/python3/dist-packages/pip/_vendor"
if _pip_vendor not in sys.path:
    sys.path.insert(0, _pip_vendor)

from rich.console import Console
from rich.table   import Table
from rich.panel   import Panel
from rich.text    import Text
from rich.columns import Columns
from rich.align   import Align
from rich.rule    import Rule
from rich.layout  import Layout
from rich.live    import Live
from rich.padding import Padding
from rich.theme   import Theme
from rich.spinner import Spinner
from rich.style   import Style
from rich         import box

sys.path.insert(0, os.path.dirname(__file__))
from data_pipeline import Database, fetch_and_store, TICKERS, SECTOR_MAP, DB_PATH
from pca_engine    import compute_pca, save_pca_run, portfolio_risk_decomposition

# ──────────────────────────────────────────────────────────
#  Theme & palette
# ──────────────────────────────────────────────────────────
THEME = Theme({
    "hdr":      "bold white on #1a1a2e",
    "pc1":      "bold #00d4ff",
    "pc2":      "bold #ffd700",
    "pc3":      "bold #ff6eb4",
    "pos":      "#00e676",
    "neg":      "#ff5252",
    "dim":      "#6c7a89",
    "accent":   "#ffd700",
    "border1":  "#00d4ff",
    "border2":  "#ffd700",
    "border3":  "#ff6eb4",
    "borderg":  "#00e676",
    "title":    "bold #e0e0e0",
    "muted":    "#9e9e9e",
    "stat":     "bold #ffffff",
})

PC_COLS   = ["pc1", "pc2", "pc3"]
PC_HEX    = ["#00d4ff", "#ffd700", "#ff6eb4"]
BORDERS   = ["border1", "border2", "border3"]
GRAD_FULL = "█"; GRAD_MED = "▓"; GRAD_LOW = "▒"; GRAD_EMPTY = "░"

# ──────────────────────────────────────────────────────────
#  Sparkline / mini bar helpers
# ──────────────────────────────────────────────────────────
SPARK_CHARS = "▁▂▃▄▅▆▇█"

def sparkline(values, width=20):
    if not values: return Text("─" * width, style="dim")
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    txt = Text()
    n = len(SPARK_CHARS) - 1
    for v in values[-width:]:
        idx = int((v - mn) / rng * n)
        lvl = idx / n
        if lvl > 0.75:   style = "pos"
        elif lvl > 0.4:  style = "accent"
        else:             style = "neg"
        txt.append(SPARK_CHARS[idx], style=style)
    return txt


def hbar(val, max_val, width=30, style="pc1", show_tip=True):
    """Gradient horizontal bar."""
    if max_val == 0: max_val = 1
    ratio  = abs(val) / max_val
    filled = int(ratio * width)
    empty  = width - filled
    t = Text()
    # gradient tip
    if filled > 0:
        t.append(GRAD_FULL * max(0, filled - 2), style=style)
        if filled >= 2: t.append(GRAD_MED, style=style)
        if filled >= 1: t.append(GRAD_LOW, style=style)
    t.append(GRAD_EMPTY * empty, style="dim")
    return t


def signed_hbar(val, max_val, width=26):
    """Bidirectional bar centred at 0."""
    half   = width // 2
    ratio  = abs(val) / max_val if max_val else 0
    filled = int(ratio * half)
    t = Text()
    if val >= 0:
        t.append(" " * half, style="")
        t.append("│", style="dim")
        t.append(GRAD_FULL * filled, style="pos")
        t.append(GRAD_EMPTY * (half - filled), style="dim")
    else:
        t.append(GRAD_EMPTY * (half - filled), style="dim")
        t.append(GRAD_FULL * filled, style="neg")
        t.append("│", style="dim")
        t.append(" " * half, style="")
    return t

# ──────────────────────────────────────────────────────────
#  Header banner
# ──────────────────────────────────────────────────────────
def make_header(result, risk, source, run_id, active_tab):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d  %H:%M UTC")

    # Title line
    title = Text()
    title.append("  ◈ ", style="pc1")
    title.append("PCA ", style="bold #00d4ff")
    title.append("Portfolio Risk Decomposition", style="bold white")
    title.append("  ◈", style="pc1")

    # Stats row
    stats = Text()
    def stat(label, val, sep="  ·  "):
        stats.append(f" {label} ", style="dim")
        stats.append(val, style="stat")
        stats.append(sep, style="dim")

    stat("Stocks",     str(len(result.tickers)))
    stat("Days",       str(len(result.returns)))
    stat("Ann. Vol",   f"{risk['total_vol_ann']:.1f}%")
    stat("Top-3 Expl", f"{result.cumulative_var[2]*100:.1f}%")
    stat("Source",     source)
    stat("Run",        f"#{run_id}", sep="")

    # Tab bar
    tabs = Text()
    tab_defs = [
        ("1", " 📊 Overview ", "border1"),
        ("2", " 🔬 Components ", "border2"),
        ("3", " 🌡  Correlation ", "border3"),
    ]
    tabs.append("  ", style="")
    for key, label, style in tab_defs:
        is_active = str(active_tab) == key
        if is_active:
            tabs.append(f"[{key}]", style="dim")
            tabs.append(label, style=f"bold white on #{style.replace('border','')}")
        else:
            tabs.append(f"[{key}]", style="dim")
            tabs.append(label, style=f"{style} on #1a1a2e")
        tabs.append("  ", style="")

    inner = Table.grid(padding=(0, 1))
    inner.add_column()
    inner.add_row(Align(title, align="center"))
    inner.add_row(Align(stats, align="center"))
    inner.add_row(Align(tabs,  align="center"))

    return Panel(inner, border_style="pc1", padding=(0, 2),
                 style="on #0d0d1a")


# ──────────────────────────────────────────────────────────
#  TAB 1 — Overview
# ──────────────────────────────────────────────────────────
def make_scree(result):
    n     = min(12, len(result.tickers))
    evars = result.explained_var[:n]
    cvar  = result.cumulative_var[:n]
    maxv  = evars[0]

    t = Table(box=box.SIMPLE, show_header=True,
              header_style="dim", expand=True)
    t.add_column("PC",        style="muted",  width=5,  justify="right")
    t.add_column("Variance",  width=34)
    t.add_column("Indiv %",   justify="right", width=8,  style="white")
    t.add_column("Cumul %",   justify="right", width=8,  style="muted")
    t.add_column("Label",     style="dim",     width=22)

    labels = result.component_labels + [f"PC{i+1}" for i in range(3, n)]
    for i in range(n):
        col   = PC_COLS[i] if i < 3 else "dim"
        cumul_style = "pos" if cvar[i] > 0.8 else ("accent" if cvar[i] > 0.5 else "muted")
        t.add_row(
            Text(f"PC{i+1}", style=col),
            hbar(evars[i], maxv, width=30, style=col),
            Text(f"{evars[i]*100:.2f}%", style=col),
            Text(f"{cvar[i]*100:.1f}%",  style=cumul_style),
            Text(labels[i].split("—")[-1].strip() if i < 3 else "", style="dim"),
        )

    return Panel(t,
        title="[bold]Scree Plot  ·  Explained Variance per Principal Component[/bold]",
        border_style="border1", padding=(0, 1))


def make_risk_decomp(risk, result):
    total_vol = risk["total_vol_ann"]

    t = Table(box=box.SIMPLE, show_header=True,
              header_style="dim", expand=True)
    t.add_column("Factor",    width=28)
    t.add_column("Breakdown", width=34)
    t.add_column("Ann. Vol",  justify="right", width=9)
    t.add_column("Share",     justify="right", width=8)

    # Total row
    t.add_row(
        Text("◆ Total Portfolio", style="bold white"),
        hbar(1.0, 1.0, width=32, style="white"),
        Text(f"{total_vol:.2f}%", style="bold white"),
        Text("100%", style="bold white"),
    )
    t.add_row("", "", "", "")  # spacer

    pc_labels = ["Market / Systematic", "Sector / Style", "Idiosyncratic"]
    pc_icons  = ["◉", "◈", "◇"]
    for k in range(3):
        pct  = risk["pct_explained"][k]
        vol  = risk["component_vols"][k]
        col  = PC_COLS[k]
        t.add_row(
            Text(f"{pc_icons[k]} {pc_labels[k]}", style=col),
            hbar(pct, 100, width=32, style=col),
            Text(f"{vol:.2f}%",  style=col),
            Text(f"{pct:.1f}%", style=col),
        )

    t.add_row(
        Text("◌ Residual",  style="dim"),
        hbar(risk["pct_residual"], 100, width=32, style="dim"),
        Text(f"{math.sqrt(risk['residual_var']*252)*100:.2f}%", style="dim"),
        Text(f"{risk['pct_residual']:.1f}%", style="dim"),
    )

    return Panel(t,
        title="[bold]Portfolio Risk Decomposition  ·  Equal Weight[/bold]",
        border_style="borderg", padding=(0, 1))


def make_cumvar_chart(result):
    n      = min(15, len(result.tickers))
    cvar   = result.cumulative_var[:n]
    labels = [f"PC{i+1}" for i in range(n)]

    t = Table.grid(padding=(0, 1))
    t.add_column(width=5,  justify="right")
    t.add_column(width=50)
    t.add_column(width=8,  justify="right")

    for i in range(n):
        col   = PC_COLS[i] if i < 3 else "dim"
        ratio = cvar[i]
        filled = int(ratio * 48)
        bar    = Text()
        bar.append(GRAD_FULL * min(filled, 48), style="pos" if ratio > 0.8 else ("accent" if ratio > 0.5 else col))
        bar.append(GRAD_EMPTY * (48 - filled),  style="dim")
        bar.append(f" {ratio*100:.0f}%", style="muted")
        t.add_row(Text(labels[i], style=col), bar, Text(""))

    return Panel(t,
        title="[bold]Cumulative Explained Variance[/bold]",
        border_style="borderg", padding=(0, 1))


def render_tab1(result, risk):
    return [
        Columns([make_scree(result), make_risk_decomp(risk, result)],
                equal=True, expand=True),
        make_cumvar_chart(result),
    ]


# ──────────────────────────────────────────────────────────
#  TAB 2 — Component Loadings
# ──────────────────────────────────────────────────────────
def make_loading_panel(result, k):
    vecs   = result.eigenvectors[:, k]
    items  = sorted(
        [(result.tickers[i], float(vecs[i])) for i in range(len(result.tickers))],
        key=lambda x: abs(x[1]), reverse=True,
    )
    max_abs = max(abs(x[1]) for x in items)

    pc_icons = ["◉ Market / Systematic", "◈ Sector / Style", "◇ Idiosyncratic"]
    evpct    = result.explained_var[k] * 100

    t = Table(box=box.SIMPLE, show_header=True,
              header_style="dim", expand=True)
    t.add_column("Ticker",  width=7,  style="white")
    t.add_column("Sector",  width=13, style="muted")
    t.add_column("Loading", width=8,  justify="right")
    t.add_column("Direction & Magnitude", width=30)

    col = PC_COLS[k]
    for rank, (ticker, val) in enumerate(items):
        sign_col = "pos" if val >= 0 else "neg"
        sign_sym = "▲" if val >= 0 else "▼"
        bar = signed_hbar(val, max_abs, width=28)
        style = col if rank < 3 else ("white" if rank < 8 else "dim")
        t.add_row(
            Text(ticker, style=style),
            Text(SECTOR_MAP.get(ticker, "—"), style="muted"),
            Text(f"{val:+.4f}", style=sign_col),
            bar,
        )

    summary  = Text()
    pos_cnt  = sum(1 for _, v in items if v > 0)
    neg_cnt  = len(items) - pos_cnt
    summary.append(f"  ↑ {pos_cnt} positive  ", style="pos")
    summary.append(f"↓ {neg_cnt} negative  ", style="neg")
    summary.append(f"│  Explains {evpct:.2f}% of variance", style="dim")

    label = result.component_labels[k] if k < len(result.component_labels) else f"PC{k+1}"
    inner = Table.grid()
    inner.add_row(t)
    inner.add_row(summary)

    return Panel(inner,
        title=f"[{col}]PC{k+1}  ·  {label.split('—')[-1].strip()}[/{col}]",
        border_style=BORDERS[k], padding=(0, 1))


def make_factor_scores(result):
    """Mini sparklines of first 3 PC scores over time."""
    T = len(result.returns)
    R_c = result.returns.values - result.returns.values.mean(axis=0)
    scores = R_c @ result.eigenvectors[:, :3]

    t = Table(box=box.SIMPLE, show_header=True,
              header_style="dim", expand=True)
    t.add_column("Factor",     width=28)
    t.add_column("Score time-series (last 60 days)", width=62)
    t.add_column("Last",       width=8, justify="right")
    t.add_column("Std",        width=8, justify="right")

    for k in range(3):
        col   = PC_COLS[k]
        s     = scores[:, k]
        label = result.component_labels[k].split("—")[-1].strip()
        last  = s[-1]
        std_  = s.std()
        t.add_row(
            Text(f"PC{k+1}  {label}", style=col),
            sparkline(s.tolist(), width=60),
            Text(f"{last:+.4f}", style="pos" if last >= 0 else "neg"),
            Text(f"{std_:.4f}",  style="muted"),
        )

    return Panel(t,
        title="[bold]Factor Score Time-Series  ·  Trailing 252 Days[/bold]",
        border_style="dim", padding=(0, 1))


def render_tab2(result):
    return [
        Columns([
            make_loading_panel(result, 0),
            make_loading_panel(result, 1),
            make_loading_panel(result, 2),
        ], equal=True, expand=True),
        make_factor_scores(result),
    ]


# ──────────────────────────────────────────────────────────
#  TAB 3 — Correlation heatmap + sector summary
# ──────────────────────────────────────────────────────────
def make_heatmap(result):
    cov  = result.cov_matrix
    std  = np.sqrt(np.diag(cov))
    corr = cov / np.outer(std, std)
    corr = np.clip(corr, -1, 1)
    tickers = result.tickers

    # gradient: negative=red, zero=dim, positive=green
    def cell(v, diag=False):
        if diag:
            return Text("██", style="bold white")
        if v >  0.7: return Text("██", style="#00e676")
        if v >  0.4: return Text("██", style="#69f0ae")
        if v >  0.1: return Text("██", style="#b9f6ca")
        if v > -0.1: return Text("░░", style="dim")
        if v > -0.4: return Text("██", style="#ff8a80")
        return          Text("██", style="#ff5252")

    # Build table
    t = Table.grid(padding=(0, 0))
    # header
    hrow = Text("       ")
    for tk in tickers:
        hrow.append(f" {tk[:4]:4}", style="dim")
    t.add_row(hrow)

    for i, rtk in enumerate(tickers):
        row = Text(f" {rtk:5} ")
        for j in range(len(tickers)):
            row.append_text(cell(corr[i, j], i == j))
            row.append(" ", style="")
        t.add_row(row)

    # Legend
    legend = Text("  Legend: ")
    for label, style in [("High +", "#00e676"), ("Med +", "#69f0ae"),
                          ("Low", "#b9f6ca"), ("~0", "dim"),
                          ("Low −", "#ff8a80"), ("High −", "#ff5252"),
                          ("Self", "bold white")]:
        legend.append("██ ", style=style)
        legend.append(f"{label}  ", style="muted")

    inner = Table.grid()
    inner.add_row(Padding(t, (1, 2)))
    inner.add_row(Padding(legend, (0, 2)))

    return Panel(inner,
        title="[bold]Asset Correlation Matrix  ·  Sample Covariance Derived[/bold]",
        border_style="border3", padding=(0, 1))


def make_sector_stats(result):
    """Per-sector average correlation and vol."""
    sectors = sorted(set(SECTOR_MAP.values()))
    cov  = result.cov_matrix
    std  = np.sqrt(np.diag(cov))
    corr = np.clip(cov / np.outer(std, std), -1, 1)

    t = Table(box=box.SIMPLE, show_header=True,
              header_style="dim", expand=True)
    t.add_column("Sector",      width=14)
    t.add_column("Stocks",      width=7, justify="right")
    t.add_column("Avg Corr",    width=10, justify="right")
    t.add_column("Avg Ann.Vol", width=12, justify="right")
    t.add_column("Intra Corr",  width=30)

    for sec in sectors:
        idxs = [i for i, tk in enumerate(result.tickers)
                if SECTOR_MAP.get(tk) == sec]
        if not idxs: continue
        vols      = [std[i] * math.sqrt(252) * 100 for i in idxs]
        avg_vol   = sum(vols) / len(vols)
        if len(idxs) > 1:
            pairs = [(i, j) for i in idxs for j in idxs if i < j]
            avg_c = sum(corr[i, j] for i, j in pairs) / len(pairs)
        else:
            avg_c = 1.0

        col = "pos" if avg_c < 0.5 else ("accent" if avg_c < 0.75 else "neg")
        t.add_row(
            Text(sec, style="white"),
            Text(str(len(idxs)), style="muted"),
            Text(f"{avg_c:.3f}", style=col),
            Text(f"{avg_vol:.1f}%", style="muted"),
            hbar(avg_c, 1.0, width=26, style=col),
        )

    return Panel(t,
        title="[bold]Sector Summary  ·  Average Intra-Sector Correlation[/bold]",
        border_style="border2", padding=(0, 1))


def render_tab3(result):
    return [
        Columns([make_heatmap(result), make_sector_stats(result)],
                equal=False, expand=True),
    ]


# ──────────────────────────────────────────────────────────
#  Footer
# ──────────────────────────────────────────────────────────
def make_footer(active_tab):
    keys = [
        ("[1]", "Overview"),
        ("[2]", "Components"),
        ("[3]", "Correlation"),
        ("[r]", "Refresh"),
        ("[q]", "Quit"),
    ]
    t = Text()
    for k, label in keys:
        t.append(f" {k}", style="accent")
        t.append(f" {label}  ", style="dim")

    t.append("│  ", style="dim")
    t.append("numpy.linalg.eigh eigendecomposition  ", style="dim")
    t.append("│  ", style="dim")
    t.append(f"DB: {DB_PATH}", style="dim")

    return Panel(Align(t, align="center"), border_style="dim",
                 style="on #0d0d1a", padding=(0, 1))


# ──────────────────────────────────────────────────────────
#  Main render
# ──────────────────────────────────────────────────────────
def render(console, result, risk, source, run_id, tab):
    console.clear()
    console.print(make_header(result, risk, source, run_id, tab))

    if tab == 1:
        for block in render_tab1(result, risk):
            console.print(block)
    elif tab == 2:
        for block in render_tab2(result):
            console.print(block)
    elif tab == 3:
        for block in render_tab3(result):
            console.print(block)

    console.print(make_footer(tab))


# ──────────────────────────────────────────────────────────
#  Animated loading screen
# ──────────────────────────────────────────────────────────
def loading_screen(console, msg):
    console.clear()
    t = Table.grid(expand=True)
    t.add_column(justify="center")
    t.add_row("")
    t.add_row("")
    t.add_row(Text("◈  PCA Portfolio Risk Dashboard  ◈", style="bold #00d4ff"))
    t.add_row("")
    t.add_row(Text(msg, style="dim"))
    t.add_row("")
    bar = Text()
    bar.append("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓", style="#00d4ff")
    bar.append("░░░░░░░░░░░░░░░░░░░░", style="dim")
    t.add_row(bar)
    console.print(Panel(t, border_style="#00d4ff",
                        style="on #0d0d1a", padding=(2, 4)))


# ──────────────────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────────────────
def run_dashboard():
    console = Console(
        force_terminal=True,
        color_system="truecolor",
        theme=THEME,
    )
    db  = Database(DB_PATH)
    tab = 1

    def do_run(force=False):
        loading_screen(console, "Fetching price data from pipeline…")
        price_df, source = fetch_and_store(db, force_refresh=force)
        loading_screen(console, "Running eigenvalue decomposition…")
        result = compute_pca(price_df, n_components=3)
        run_id = save_pca_run(db, result)
        risk   = portfolio_risk_decomposition(result)
        return result, risk, source, run_id

    result, risk, source, run_id = do_run()
    render(console, result, risk, source, run_id, tab)

    if not sys.stdin.isatty():
        return

    import termios, tty

    def getch():
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    while True:
        try:
            ch = getch()
        except Exception:
            break

        if ch == "q":
            console.clear()
            goodbye = Text()
            goodbye.append("\n  ◈ ", style="pc1")
            goodbye.append("Thanks for using PCA Dashboard", style="bold white")
            goodbye.append("  ◈\n", style="pc1")
            console.print(Panel(Align(goodbye, align="center"),
                                border_style="pc1", style="on #0d0d1a"))
            break
        elif ch == "r":
            result, risk, source, run_id = do_run(force=True)
            render(console, result, risk, source, run_id, tab)
        elif ch in ("1", "2", "3"):
            tab = int(ch)
            render(console, result, risk, source, run_id, tab)


if __name__ == "__main__":
    run_dashboard()