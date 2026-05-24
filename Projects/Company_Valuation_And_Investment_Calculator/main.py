"""
Company Valuation & Investment Dashboard — TUI
"""
import asyncio
import math
import os
import sys
from datetime import datetime
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    LoadingIndicator,
    Markdown,
    ProgressBar,
    RichLog,
    Rule,
    Select,
    Static,
    TabbedContent,
    TabPane,
)
from textual import work
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from rich import box

import data_fetcher as df
import db_manager as db
import finance_calc as fc


# ── Colour palette ─────────────────────────────────────────────────────────────
ACCENT   = "bright_cyan"
POSITIVE = "bright_green"
NEGATIVE = "bright_red"
NEUTRAL  = "bright_yellow"
DIM      = "grey70"


def fmt_currency(val: float, currency: str = "$", decimals: int = 2) -> str:
    if val is None:
        return "N/A"
    if abs(val) >= 1e12:
        return f"{currency}{val/1e12:.2f}T"
    if abs(val) >= 1e9:
        return f"{currency}{val/1e9:.2f}B"
    if abs(val) >= 1e6:
        return f"{currency}{val/1e6:.2f}M"
    return f"{currency}{val:,.{decimals}f}"


def fmt_pct(val: float) -> str:
    if val is None:
        return "N/A"
    return f"{val:.2f}%"


def fmt_num(val: float) -> str:
    if val is None:
        return "N/A"
    return f"{val:,.2f}"


def sparkline(values: list[float], width: int = 20) -> str:
    """Simple ASCII sparkline using block chars."""
    blocks = "▁▂▃▄▅▆▇█"
    if not values or len(values) < 2:
        return "─" * width
    mn, mx = min(values), max(values)
    rng = mx - mn or 1
    sample = values[::max(1, len(values) // width)][:width]
    return "".join(blocks[min(int((v - mn) / rng * 7), 7)] for v in sample)


def mini_bar_chart(labels: list, values: list[float], width: int = 40) -> str:
    """Horizontal bar chart as rich markup string."""
    if not values:
        return ""
    mx = max(abs(v) for v in values) or 1
    lines = []
    for label, val in zip(labels, values):
        bar_len = int(abs(val) / mx * (width - 2))
        bar = ("█" * bar_len).ljust(width - 2)
        colour = POSITIVE if val >= 0 else NEGATIVE
        lines.append(f"[{DIM}]{label[:12]:>12}[/{DIM}] [{colour}]{bar}[/{colour}] [{colour}]{fmt_currency(val)}[/{colour}]")
    return "\n".join(lines)


# ── Modal: Add Company ─────────────────────────────────────────────────────────

class AddCompanyModal(ModalScreen):
    CSS = """
    AddCompanyModal {
        align: center middle;
    }
    #modal-container {
        width: 60;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 2 4;
    }
    #modal-title {
        text-align: center;
        color: $accent;
        margin-bottom: 1;
        text-style: bold;
    }
    #ticker-input {
        margin: 1 0;
    }
    #modal-buttons {
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="modal-container"):
            yield Label("➕  ADD COMPANY", id="modal-title")
            yield Rule()
            yield Label("Enter stock ticker symbol (e.g. AAPL, MSFT, INFY):")
            yield Input(placeholder="TICKER", id="ticker-input")
            yield Label("", id="modal-error")
            with Horizontal(id="modal-buttons"):
                yield Button("Add Company", variant="primary", id="btn-add")
                yield Button("Cancel", variant="default", id="btn-cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-cancel":
            self.dismiss(None)
        elif event.button.id == "btn-add":
            ticker = self.query_one("#ticker-input", Input).value.strip().upper()
            if not ticker:
                self.query_one("#modal-error", Label).update("[red]Please enter a ticker symbol.[/red]")
                return
            self.dismiss(ticker)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        ticker = event.value.strip().upper()
        if ticker:
            self.dismiss(ticker)


# ── Mini ASCII Chart widget ────────────────────────────────────────────────────

class ChartWidget(Static):
    """Renders a price history ASCII chart."""

    DEFAULT_CSS = """
    ChartWidget {
        height: 14;
        border: solid $accent;
        padding: 0 1;
    }
    """

    def render_chart(self, prices: list[float], title: str = "Price History") -> str:
        if not prices or len(prices) < 2:
            return f"[{DIM}]No price data available[/{DIM}]"

        # Sample to fit width
        w = 70
        h = 10
        sample = prices[::max(1, len(prices) // w)][-w:]
        mn, mx = min(sample), max(sample)
        rng = mx - mn or 1

        # Build grid
        grid = [[" "] * len(sample) for _ in range(h)]
        prev_row = None
        for col, price in enumerate(sample):
            row = h - 1 - int((price - mn) / rng * (h - 1))
            row = max(0, min(h - 1, row))
            grid[row][col] = "●"
            if prev_row is not None:
                # Draw vertical line between points
                lo, hi = min(row, prev_row), max(row, prev_row)
                for r in range(lo + 1, hi):
                    grid[r][col] = "│"
            prev_row = row

        colour = POSITIVE if sample[-1] >= sample[0] else NEGATIVE
        lines = []
        lines.append(f"[{ACCENT}]{title}[/{ACCENT}]  [{colour}]{fmt_currency(sample[0])}[/{colour}] → [{colour}]{fmt_currency(sample[-1])}[/{colour}]")
        for i, row in enumerate(grid):
            # Y-axis label
            price_at = mx - (i / (h - 1)) * rng
            label = f"[{DIM}]{fmt_currency(price_at, decimals=0):>8}[/{DIM}]"
            row_str = "".join(f"[{colour}]{c}[/{colour}]" if c in "●│" else f"[{DIM}]{c}[/{DIM}]" for c in row)
            lines.append(f"{label} │{row_str}")
        lines.append(f"[{DIM}]{'─'*9}┴{'─'*len(sample)}[/{DIM}]")
        return "\n".join(lines)


# ── Overview Panel ─────────────────────────────────────────────────────────────

class OverviewPanel(Static):
    DEFAULT_CSS = """
    OverviewPanel { height: auto; padding: 0 1; }
    """

    def render_overview(self, ticker: str, profile: dict, fin: dict, price: float, valuation: dict) -> str:
        if not profile:
            return f"[{DIM}]No data loaded yet. Press [R] to refresh.[/{DIM}]"

        name     = profile.get("name", ticker)
        exchange = profile.get("exchange", "")
        country  = profile.get("country", "")
        sector   = profile.get("sector", "") or fin.get("sector", "")
        mktcap   = profile.get("market_cap", 0) or fin.get("market_cap", 0)
        shares   = profile.get("shares_out", 0) or fin.get("shares", 0)
        currency = profile.get("currency", "USD")

        iv = valuation.get("intrinsic_value", 0)
        up = valuation.get("upside_pct", 0)
        label = valuation.get("valuation_label", "")
        wacc = valuation.get("wacc", 0)

        # Price change colour
        price_colour = ACCENT

        lines = [
            f"[bold {ACCENT}]{'═'*68}[/bold {ACCENT}]",
            f"  [bold white]{name}[/bold white]  [bold {NEUTRAL}]({ticker})[/bold {NEUTRAL}]  [{DIM}]{exchange} · {country}[/{DIM}]",
            f"  [{DIM}]Sector:[/{DIM}] {sector}",
            f"[bold {ACCENT}]{'─'*68}[/bold {ACCENT}]",
            f"  [bold {ACCENT}]Market Price[/bold {ACCENT}]   [{price_colour}]{fmt_currency(price, currency[0] if currency else '$')}[/{price_colour}]"
            + (f"        [bold]Intrinsic Value[/bold]  [{POSITIVE if up>0 else NEGATIVE}]{fmt_currency(iv, currency[0] if currency else '$')}[/{POSITIVE if up>0 else NEGATIVE}]" if iv else ""),
            f"  [bold {ACCENT}]Market Cap[/bold {ACCENT}]     {fmt_currency(mktcap)}"
            + f"          [bold]Upside / Downside[/bold] [{POSITIVE if up>0 else NEGATIVE}]{fmt_pct(up)}[/{POSITIVE if up>0 else NEGATIVE}]",
            f"  [bold {ACCENT}]Shares Out[/bold {ACCENT}]     {fmt_currency(shares, '', 0)}"
            + (f"   [{NEUTRAL}]WACC[/{NEUTRAL}] {fmt_pct(wacc*100)}" if wacc else ""),
            f"",
            (f"  {label}" if label else "  [italic grey50]Run valuation to see rating[/italic grey50]"),
            f"[bold {ACCENT}]{'═'*68}[/bold {ACCENT}]",
        ]
        return "\n".join(lines)


# ── Main Dashboard Screen ──────────────────────────────────────────────────────

class DashboardScreen(Screen):
    BINDINGS = [
        Binding("r", "refresh_data", "Refresh", priority=True),
        Binding("a", "add_company", "Add Company", priority=True),
        Binding("v", "run_valuation", "Run Valuation", priority=True),
        Binding("q", "quit_app", "Quit", priority=True),
    ]

    CSS = """
    DashboardScreen {
        layout: grid;
        grid-size: 1;
    }

    #sidebar {
        width: 22;
        background: $surface;
        border-right: solid $accent;
        padding: 1;
    }

    #main-area {
        layout: vertical;
    }

    #top-bar {
        height: auto;
        padding: 0;
    }

    .sidebar-title {
        text-align: center;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .sidebar-ticker {
        padding: 0 1;
        height: 3;
        border: solid transparent;
    }

    .sidebar-ticker:hover {
        border: solid $accent;
    }

    .sidebar-ticker.active {
        border: solid $accent;
        background: $boost;
    }

    #btn-add-company {
        margin-top: 1;
        width: 100%;
    }

    #status-bar {
        height: 1;
        color: $text-muted;
        padding: 0 1;
        background: $surface;
    }

    TabbedContent {
        height: 1fr;
    }

    .panel-label {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }

    .kpi-grid {
        layout: grid;
        grid-size: 4;
        grid-gutter: 1;
        height: auto;
        margin: 1 0;
    }

    .kpi-box {
        border: solid $accent;
        padding: 1;
        height: 7;
        background: $surface;
    }

    .kpi-value {
        text-align: center;
        text-style: bold;
        color: ansi_bright_white;
    }

    .kpi-label {
        text-align: center;
        color: $text-muted;
    }

    ScrollableContainer {
        scrollbar-gutter: stable;
    }

    #log-area {
        height: 1fr;
        border: solid $accent;
        padding: 1;
    }

    LoadingIndicator {
        background: $surface;
    }

    .section-header {
        background: $boost;
        color: $accent;
        text-style: bold;
        padding: 0 1;
        margin: 1 0 0 0;
    }
    """

    active_ticker: reactive[str] = reactive("")
    status_msg: reactive[str]    = reactive("Ready — press [A] to add a company")
    is_loading: reactive[bool]   = reactive(False)

    def __init__(self):
        super().__init__()
        self._companies: list[str] = db.list_companies()
        self._loaded_data: dict    = {}   # ticker → {profile, metrics, price, valuation, history}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            # Sidebar
            with Vertical(id="sidebar"):
                yield Label("📊 PORTFOLIO", classes="sidebar-title")
                yield Rule()
                yield ScrollableContainer(id="sidebar-list")
                yield Button("➕ Add Company", id="btn-add-company", variant="primary")

            # Main content
            with Vertical(id="main-area"):
                yield Static(id="status-bar")
                with TabbedContent():
                    with TabPane("📈 Overview", id="tab-overview"):
                        with ScrollableContainer():
                            yield OverviewPanel(id="overview-panel")
                            yield Static(id="chart-area")
                            yield Static(id="kpi-area")

                    with TabPane("💰 Valuation", id="tab-valuation"):
                        with ScrollableContainer():
                            yield Static(id="valuation-panel")

                    with TabPane("📐 WACC / Capital", id="tab-wacc"):
                        with ScrollableContainer():
                            yield Static(id="wacc-panel")

                    with TabPane("📅 TVM / DCF", id="tab-dcf"):
                        with ScrollableContainer():
                            yield Static(id="dcf-panel")

                    with TabPane("📊 NPV / IRR", id="tab-npv"):
                        with ScrollableContainer():
                            yield Static(id="npv-panel")

                    with TabPane("💵 Dividends", id="tab-div"):
                        with ScrollableContainer():
                            yield Static(id="div-panel")

                    with TabPane("🔍 Sensitivity", id="tab-sens"):
                        with ScrollableContainer():
                            yield Static(id="sens-panel")

                    with TabPane("📋 Log", id="tab-log"):
                        yield RichLog(id="log-area", highlight=True, markup=True)

        yield Footer()

    def on_mount(self) -> None:
        self._rebuild_sidebar()
        if self._companies:
            self._select_company(self._companies[0])
        self._update_status("Press [A] to add a company  ·  [R] to refresh  ·  [V] to run valuation")

    def _rebuild_sidebar(self) -> None:
        """Full rebuild — only mounts tickers not already present."""
        sidebar = self.query_one("#sidebar-list", ScrollableContainer)
        for t in self._companies:
            if not sidebar.query(f"#company-{t}"):
                btn = Button(f"[bold]{t}[/bold]", id=f"company-{t}",
                             classes="sidebar-ticker" + (" active" if t == self.active_ticker else ""))
                sidebar.mount(btn)

    def _add_ticker_to_sidebar(self, ticker: str) -> None:
        """Safely append a single new ticker button (no removal needed)."""
        sidebar = self.query_one("#sidebar-list", ScrollableContainer)
        if not sidebar.query(f"#company-{ticker}"):
            btn = Button(f"[bold]{ticker}[/bold]", id=f"company-{ticker}",
                         classes="sidebar-ticker")
            sidebar.mount(btn)

    def _select_company(self, ticker: str) -> None:
        old = self.active_ticker
        self.active_ticker = ticker
        # update styling
        if old:
            try:
                self.query_one(f"#company-{old}", Button).remove_class("active")
            except Exception:
                pass
        try:
            self.query_one(f"#company-{ticker}", Button).add_class("active")
        except Exception:
            pass
        self._render_cached(ticker)

    def _update_status(self, msg: str) -> None:
        self.query_one("#status-bar", Static).update(f"[{DIM}] {msg} [/{DIM}]")

    def _log(self, msg: str) -> None:
        try:
            log = self.query_one("#log-area", RichLog)
            ts  = datetime.now().strftime("%H:%M:%S")
            log.write(f"[{DIM}][{ts}][/{DIM}] {msg}")
        except Exception:
            pass

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "btn-add-company":
            self.action_add_company()
        elif bid.startswith("company-"):
            ticker = bid.replace("company-", "")
            self._select_company(ticker)
            if ticker not in self._loaded_data:
                self.action_refresh_data()

    def action_add_company(self) -> None:
        self.app.push_screen(AddCompanyModal(), self._on_add_company)

    def _on_add_company(self, ticker: str | None) -> None:
        if not ticker:
            return
        ticker = ticker.upper()
        if ticker not in self._companies:
            self._companies.append(ticker)
            db.init_company_db(ticker)
            self._add_ticker_to_sidebar(ticker)
        self._select_company(ticker)
        self.fetch_company_data(ticker)

    def action_refresh_data(self) -> None:
        if self.active_ticker:
            self.fetch_company_data(self.active_ticker)

    def action_run_valuation(self) -> None:
        if self.active_ticker:
            data = self._loaded_data.get(self.active_ticker, {})
            if data:
                self._run_valuation_for(self.active_ticker, data)
            else:
                self.fetch_company_data(self.active_ticker)

    def action_quit_app(self) -> None:
        self.app.exit()

    # ── Data fetching (async worker) ──────────────────────────────────────────

    @work(thread=True)
    def fetch_company_data(self, ticker: str) -> None:
        self.app.call_from_thread(self._update_status, f"⟳  Fetching data for {ticker}...")
        self.app.call_from_thread(self._log, f"[{ACCENT}]Starting data fetch for [{NEUTRAL}]{ticker}[/{NEUTRAL}]...[/{ACCENT}]")

        try:
            # Initialise DB
            db.init_company_db(ticker)

            # 1. Company profile
            self.app.call_from_thread(self._log, "  ↪ Fetching company profile...")
            profile_raw = df.get_company_profile(ticker)
            if profile_raw and profile_raw.get("name"):
                db.upsert_profile(ticker, profile_raw)
            profile = db.get_profile(ticker)

            # 2. Metrics
            self.app.call_from_thread(self._log, "  ↪ Fetching financial metrics...")
            metrics_raw = df.get_basic_financials(ticker)
            metrics = metrics_raw.get("metric", {}) if isinstance(metrics_raw, dict) else {}
            if metrics:
                db.upsert_metrics(ticker, metrics)
            all_metrics = db.get_all_metrics(ticker)

            # 3. Price
            self.app.call_from_thread(self._log, "  ↪ Fetching latest price...")
            quote = df.get_latest_quote(ticker)
            price = quote.get("price", 0)

            # 4. Historical bars
            self.app.call_from_thread(self._log, "  ↪ Fetching price history...")
            bars = df.get_historical_bars(ticker, days=365)
            if bars:
                db.upsert_price_history(ticker, bars)
            history = db.get_price_history(ticker)

            # 5. Dividends
            self.app.call_from_thread(self._log, "  ↪ Fetching dividends...")
            divs = df.get_dividends(ticker)
            if divs:
                db.upsert_dividends(ticker, divs)
            dividends = db.get_dividends_history(ticker)

            # 6. Peers
            self.app.call_from_thread(self._log, "  ↪ Fetching peers...")
            peers = df.get_peers(ticker)
            if peers:
                db.upsert_peers(ticker, peers)

            # 7. Recommendations / news
            recs  = df.get_recommendation_trends(ticker)

            # Consolidate
            fin = fc.derive_financials_from_metrics(
                {"metric": all_metrics}, profile_raw or {}
            )
            if price == 0 and fin.get("price", 0):
                price = fin["price"]

            data = {
                "profile":   profile,
                "metrics":   all_metrics,
                "fin":       fin,
                "price":     price,
                "history":   history,
                "dividends": dividends,
                "peers":     peers[:5] if peers else [],
                "recs":      recs[:3] if recs else [],
                "valuation": {},
            }
            self._loaded_data[ticker] = data

            # Auto-run valuation
            self.app.call_from_thread(self._log, "  ↪ Running valuation calculations...")
            self.app.call_from_thread(self._run_valuation_for, ticker, data)

            self.app.call_from_thread(self._log, f"[{POSITIVE}]✓ Data fetch complete for {ticker}[/{POSITIVE}]")
            self.app.call_from_thread(self._update_status, f"✓ {ticker} loaded · {datetime.now().strftime('%H:%M:%S')}")
            self.app.call_from_thread(self._render_cached, ticker)

        except Exception as e:
            self.app.call_from_thread(self._log, f"[{NEGATIVE}]✗ Error fetching {ticker}: {e}[/{NEGATIVE}]")
            self.app.call_from_thread(self._update_status, f"✗ Error: {e}")

    def _run_valuation_for(self, ticker: str, data: dict) -> None:
        try:
            fin   = data.get("fin", {})
            price = data.get("price", 0)
            if not fin or not price:
                return
            result = fc.run_full_valuation(fin, price)
            data["valuation"] = result

            # Save to DB
            db.save_valuation(ticker, {
                "wacc":            result["wacc"],
                "intrinsic_value": result["intrinsic_value"],
                "market_price":    price,
                "npv_project":     result["npv_project"],
                "irr_project":     result["irr_project"],
                "dcf_details":     result.get("dcf", {}),
            })
            self._render_cached(ticker)
        except Exception as e:
            self._log(f"[{NEGATIVE}]Valuation error: {e}[/{NEGATIVE}]")

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _render_cached(self, ticker: str) -> None:
        if ticker != self.active_ticker:
            return
        data = self._loaded_data.get(ticker, {})
        if not data:
            return
        profile   = data.get("profile", {})
        metrics   = data.get("metrics", {})
        fin       = data.get("fin", {})
        price     = data.get("price", 0)
        history   = data.get("history", [])
        dividends = data.get("dividends", [])
        peers     = data.get("peers", [])
        valuation = data.get("valuation", {})

        self._render_overview(ticker, profile, fin, price, valuation, history)
        self._render_valuation(ticker, valuation, fin, price)
        self._render_wacc(ticker, valuation, fin)
        self._render_dcf(ticker, valuation, fin)
        self._render_npv(ticker, valuation, fin, price)
        self._render_dividends(ticker, dividends, fin, price, peers)
        self._render_sensitivity(ticker, valuation)

    def _render_overview(self, ticker, profile, fin, price, valuation, history):
        try:
            # Overview panel
            op = self.query_one("#overview-panel", OverviewPanel)
            op.update(op.render_overview(ticker, profile, fin, price, valuation))

            # Chart
            prices = [b["close"] for b in history if b.get("close")]
            chart_html = ""
            if prices:
                cw = ChartWidget()
                chart_html = cw.render_chart(prices, f"{ticker} — 1 Year Price History")
            self.query_one("#chart-area", Static).update(chart_html or f"[{DIM}]No price history available[/{DIM}]")

            # KPIs
            kpi_lines = self._build_kpi_section(fin, price, metrics={})
            self.query_one("#kpi-area", Static).update(kpi_lines)
        except Exception as e:
            self._log(f"Overview render error: {e}")

    def _build_kpi_section(self, fin: dict, price: float, metrics: dict) -> str:
        beta      = fin.get("beta", 0)
        pe        = fin.get("pe_ratio", 0)
        eps       = fin.get("eps_ttm", 0)
        div_yld   = fin.get("div_yield", 0)
        mktcap    = fin.get("market_cap", 0)
        revenue   = fin.get("revenue_ttm", 0)
        net_inc   = fin.get("net_income_ttm", 0)
        fcf       = fin.get("fcf_ttm", 0)
        debt      = fin.get("total_debt", 0)
        equity    = fin.get("total_equity", 0)

        kpis = [
            ("Price",       fmt_currency(price)),
            ("Market Cap",  fmt_currency(mktcap)),
            ("Revenue TTM", fmt_currency(revenue)),
            ("Net Income",  fmt_currency(net_inc)),
            ("FCF TTM",     fmt_currency(fcf)),
            ("EPS TTM",     fmt_currency(eps, "$", 2)),
            ("P/E Ratio",   fmt_num(pe)),
            ("Beta",        fmt_num(beta)),
            ("Div Yield",   fmt_pct(div_yld * 100 if div_yld and div_yld < 1 else div_yld)),
            ("Total Debt",  fmt_currency(debt)),
            ("Equity",      fmt_currency(equity)),
            ("D/E Ratio",   fmt_num(debt / equity if equity else 0)),
        ]

        rows = []
        row  = []
        for label, val in kpis:
            row.append(f"  [{DIM}]{label}[/{DIM}]\n  [bold white]{val}[/bold white]")
            if len(row) == 4:
                rows.append("  " + "    │    ".join(row))
                row = []
        if row:
            rows.append("  " + "    │    ".join(row))

        header = f"\n[bold {ACCENT}]── Key Metrics ──────────────────────────────────────────────────[/bold {ACCENT}]\n"
        return header + "\n".join(rows) + "\n"

    def _render_valuation(self, ticker, valuation, fin, price):
        if not valuation:
            self.query_one("#valuation-panel", Static).update(f"[{DIM}]No valuation data. Press [V] to run.[/{DIM}]")
            return
        try:
            dcf  = valuation.get("dcf", {})
            iv   = valuation.get("intrinsic_value", 0)
            up   = valuation.get("upside_pct", 0)
            wacc = valuation.get("wacc", 0)
            ke   = valuation.get("ke", 0)
            beta = valuation.get("beta", 0)
            label = valuation.get("valuation_label", "")

            ev   = dcf.get("enterprise_value", 0)
            eq_v = dcf.get("equity_value", 0)
            pv_t = dcf.get("pv_terminal_value", 0)
            spvf = dcf.get("sum_pv_fcfs", 0)
            tv   = dcf.get("terminal_value", 0)

            colour = POSITIVE if up > 0 else NEGATIVE

            lines = [
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]COMPANY VALUATION SUMMARY — {ticker}[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*66}[/bold {ACCENT}]",
                f"",
                f"  [bold]Valuation Model:[/bold]  Discounted Cash Flow (DCF) + Terminal Value",
                f"  [bold]WACC:[/bold]             [{NEUTRAL}]{fmt_pct(wacc*100)}[/{NEUTRAL}]",
                f"  [bold]Cost of Equity:[/bold]   [{NEUTRAL}]{fmt_pct(ke*100)}[/{NEUTRAL}]  (CAPM, β={fmt_num(beta)})",
                f"",
                f"  [bold {ACCENT}]── Valuation Components ──────────────────────────────────[/bold {ACCENT}]",
                f"  PV of Projected FCFs   :  [bold]{fmt_currency(spvf)}[/bold]",
                f"  Terminal Value (Gordon) :  [bold]{fmt_currency(tv)}[/bold]",
                f"  PV of Terminal Value   :  [bold]{fmt_currency(pv_t)}[/bold]",
                f"  ───────────────────────────────────────────────────────",
                f"  Enterprise Value       :  [bold white]{fmt_currency(ev)}[/bold white]",
                f"  Less: Net Debt         :  [{NEGATIVE}]{fmt_currency(fin.get('net_debt',0))}[/{NEGATIVE}]",
                f"  Plus: Cash             :  [{POSITIVE}]{fmt_currency(fin.get('cash',0))}[/{POSITIVE}]",
                f"  ───────────────────────────────────────────────────────",
                f"  Equity Value           :  [bold white]{fmt_currency(eq_v)}[/bold white]",
                f"  Shares Outstanding     :  {fmt_currency(fin.get('shares',0), '', 0)}",
                f"",
                f"[bold {ACCENT}]{'─'*66}[/bold {ACCENT}]",
                f"  [bold]Market Price        :[/bold]  [bold white]{fmt_currency(price)}[/bold white]",
                f"  [bold]Intrinsic Value     :[/bold]  [bold {colour}]{fmt_currency(iv)}[/bold {colour}]",
                f"  [bold]Upside / Downside   :[/bold]  [bold {colour}]{fmt_pct(up)}[/bold {colour}]",
                f"",
                f"  {label}",
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
            ]
            self.query_one("#valuation-panel", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#valuation-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")

    def _render_wacc(self, ticker, valuation, fin):
        if not valuation:
            self.query_one("#wacc-panel", Static).update(f"[{DIM}]Run valuation first.[/{DIM}]")
            return
        try:
            wd = valuation.get("wacc_details", {})
            wacc = valuation.get("wacc", 0)
            ke   = valuation.get("ke", 0)
            beta = valuation.get("beta", 0)

            we   = wd.get("we", 0)
            wdp  = wd.get("wd", 0)
            kd   = wd.get("kd_after_tax", 0)
            eq_v = fin.get("total_equity", 0)
            dbt  = fin.get("total_debt", 0)
            tax  = wd.get("tax_rate", 0.25)

            # Stacked bar for capital structure
            total = eq_v + dbt
            bar_w = 50
            eq_bar = int(we * bar_w)
            dt_bar = bar_w - eq_bar

            lines = [
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]WACC & CAPITAL STRUCTURE — {ticker}[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*66}[/bold {ACCENT}]",
                f"",
                f"  [bold {ACCENT}]── CAPM: Cost of Equity ──────────────────────────────────[/bold {ACCENT}]",
                f"  Formula: Ke = Rf + β × (Rm - Rf)",
                f"  Risk-Free Rate (Rf)     :  [{NEUTRAL}]{fmt_pct(valuation.get('risk_free_rate',0.045)*100)}[/{NEUTRAL}]  (10-yr Treasury proxy)",
                f"  Beta (β)               :  [{NEUTRAL}]{fmt_num(beta)}[/{NEUTRAL}]",
                f"  Market Risk Premium    :  [{NEUTRAL}]5.50%[/{NEUTRAL}]",
                f"  ───────────────────────────────────────────────────────",
                f"  Cost of Equity (Ke)    :  [bold {POSITIVE}]{fmt_pct(ke*100)}[/bold {POSITIVE}]",
                f"",
                f"  [bold {ACCENT}]── Cost of Debt ──────────────────────────────────────────[/bold {ACCENT}]",
                f"  Total Debt             :  {fmt_currency(dbt)}",
                f"  Cost of Debt (pre-tax) :  [{NEUTRAL}]{fmt_pct(fin.get('cost_of_debt',0)*100)}[/{NEUTRAL}]",
                f"  Tax Rate               :  [{NEUTRAL}]{fmt_pct(tax*100)}[/{NEUTRAL}]",
                f"  ───────────────────────────────────────────────────────",
                f"  Cost of Debt (Kd, AT)  :  [bold {POSITIVE}]{fmt_pct(kd*100)}[/bold {POSITIVE}]",
                f"",
                f"  [bold {ACCENT}]── Capital Structure ──────────────────────────────────────[/bold {ACCENT}]",
                f"  Equity (E)             :  [{POSITIVE}]{fmt_currency(eq_v)}[/{POSITIVE}]  ({fmt_pct(we*100)} of total)",
                f"  Debt (D)               :  [{NEGATIVE}]{fmt_currency(dbt)}[/{NEGATIVE}]  ({fmt_pct(wdp*100)} of total)",
                f"  Total Capital (V)      :  {fmt_currency(total)}",
                f"",
                f"  Capital Mix:",
                f"  [{POSITIVE}]{'█'*eq_bar}[/{POSITIVE}][{NEGATIVE}]{'█'*dt_bar}[/{NEGATIVE}]  [{POSITIVE}]Equity {fmt_pct(we*100)}[/{POSITIVE}] / [{NEGATIVE}]Debt {fmt_pct(wdp*100)}[/{NEGATIVE}]",
                f"",
                f"  [bold {ACCENT}]── WACC Formula ───────────────────────────────────────────[/bold {ACCENT}]",
                f"  WACC = (E/V)×Ke + (D/V)×Kd×(1-t)",
                f"       = ({fmt_pct(we*100)} × {fmt_pct(ke*100)}) + ({fmt_pct(wdp*100)} × {fmt_pct(fin.get('cost_of_debt',0)*100)} × {fmt_pct((1-tax)*100)})",
                f"",
                f"  [bold white]WACC = [bold {ACCENT}]{fmt_pct(wacc*100)}[/bold {ACCENT}][/bold white]",
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
            ]
            self.query_one("#wacc-panel", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#wacc-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")

    def _render_dcf(self, ticker, valuation, fin):
        if not valuation:
            self.query_one("#dcf-panel", Static).update(f"[{DIM}]Run valuation first.[/{DIM}]")
            return
        try:
            dcf     = valuation.get("dcf", {})
            tvm     = valuation.get("tvm_table", [])
            wacc    = valuation.get("wacc", 0)
            gr      = valuation.get("growth_rates", [])
            tg      = valuation.get("terminal_growth", 0.025)
            base_fcf = fin.get("fcf_ttm", 0)

            header = [
                f"[bold {ACCENT}]{'═'*72}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]TVM CALCULATOR & DCF ANALYSIS — {ticker}[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*72}[/bold {ACCENT}]",
                f"",
                f"  [bold]Base FCF (TTM):[/bold]  {fmt_currency(base_fcf)}",
                f"  [bold]Discount Rate :[/bold]  {fmt_pct(wacc*100)} (WACC)",
                f"  [bold]Terminal Growth:[/bold] {fmt_pct(tg*100)}",
                f"",
                f"  [bold {ACCENT}]── Projected Free Cash Flows & TVM Table ─────────────────────────[/bold {ACCENT}]",
                f"  {'Year':>4}  {'Growth':>7}  {'FCF':>14}  {'PV (discounted)':>16}  {'FV (compounded)':>16}",
                f"  {'─'*4}  {'─'*7}  {'─'*14}  {'─'*16}  {'─'*16}",
            ]

            rows = []
            for i, item in enumerate(tvm):
                yr  = item["year"]
                fcf = item["fcf"]
                pv  = item["pv"]
                fv  = item["fv"]
                g   = gr[i] if i < len(gr) else 0
                row = f"  {yr:>4}  [{NEUTRAL}]{fmt_pct(g*100):>7}[/{NEUTRAL}]  [{ACCENT}]{fmt_currency(fcf):>14}[/{ACCENT}]  [{POSITIVE}]{fmt_currency(pv):>16}[/{POSITIVE}]  [{NEUTRAL}]{fmt_currency(fv):>16}[/{NEUTRAL}]"
                rows.append(row)

            tv_row = [
                f"  {'─'*4}  {'─'*7}  {'─'*14}  {'─'*16}  {'─'*16}",
                f"  [bold]Terminal Value (Year {len(tvm)}):[/bold]",
                f"    Gordon Growth TV    :  [{NEUTRAL}]{fmt_currency(dcf.get('terminal_value',0)):>16}[/{NEUTRAL}]",
                f"    PV of Terminal Value:  [{POSITIVE}]{fmt_currency(dcf.get('pv_terminal_value',0)):>16}[/{POSITIVE}]",
                f"    Sum PV of FCFs     :  [{POSITIVE}]{fmt_currency(dcf.get('sum_pv_fcfs',0)):>16}[/{POSITIVE}]",
                f"",
                f"  [bold {ACCENT}]── Enterprise Value Bridge ─────────────────────────────────────[/bold {ACCENT}]",
                f"  Enterprise Value :  [{ACCENT}]{fmt_currency(dcf.get('enterprise_value',0)):>14}[/{ACCENT}]",
                f"  Net Debt         :  [{NEGATIVE}]{fmt_currency(fin.get('net_debt',0)):>14}[/{NEGATIVE}]",
                f"  Cash             :  [{POSITIVE}]{fmt_currency(fin.get('cash',0)):>14}[/{POSITIVE}]",
                f"  Equity Value     :  [bold white]{fmt_currency(dcf.get('equity_value',0)):>14}[/bold white]",
                f"  Shares           :  {fmt_currency(fin.get('shares',0), '', 0):>14}",
                f"  ──────────────────────────────────",
                f"  Intrinsic/Share  :  [bold {ACCENT}]{fmt_currency(valuation.get('intrinsic_value',0)):>14}[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'═'*72}[/bold {ACCENT}]",
            ]

            content = "\n".join(header + rows + tv_row)
            self.query_one("#dcf-panel", Static).update(content)
        except Exception as e:
            self.query_one("#dcf-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")

    def _render_npv(self, ticker, valuation, fin, price):
        if not valuation:
            self.query_one("#npv-panel", Static).update(f"[{DIM}]Run valuation first.[/{DIM}]")
            return
        try:
            npv      = valuation.get("npv_project", 0)
            irr      = valuation.get("irr_project", 0) or 0.0
            wacc     = valuation.get("wacc", 0)
            cost     = valuation.get("project_cost", 0)
            proj_cfs = valuation.get("project_cfs", [])

            npv_colour = POSITIVE if npv > 0 else NEGATIVE
            irr_colour = POSITIVE if irr > wacc else NEGATIVE
            decision   = "✅ ACCEPT" if npv > 0 and irr > wacc else "❌ REJECT"

            cf_chart = mini_bar_chart(
                [f"CF{i+1}" for i in range(len(proj_cfs))],
                proj_cfs, width=40
            )

            lines = [
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]NPV & IRR ANALYSIS — Hypothetical Project ({ticker})[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*66}[/bold {ACCENT}]",
                f"",
                f"  [bold]Project Description:[/bold]",
                f"  Simulated capital project = 5% of market cap,",
                f"  generating growing annual cash flows over 7 years.",
                f"",
                f"  [bold {ACCENT}]── Project Parameters ────────────────────────────────────[/bold {ACCENT}]",
                f"  Initial Investment (C₀) :  [{NEGATIVE}]{fmt_currency(cost)}[/{NEGATIVE}]",
                f"  Project Duration        :  7 years",
                f"  Hurdle Rate (WACC)      :  [{NEUTRAL}]{fmt_pct(wacc*100)}[/{NEUTRAL}]",
                f"",
                f"  [bold {ACCENT}]── Projected Cash Inflows ────────────────────────────────[/bold {ACCENT}]",
            ]

            for i, cf in enumerate(proj_cfs):
                pv_cf = fc.present_value(cf, wacc, i + 1)
                lines.append(f"  Year {i+1}:  [{POSITIVE}]{fmt_currency(cf):>14}[/{POSITIVE}]  →  PV: [{NEUTRAL}]{fmt_currency(pv_cf):>14}[/{NEUTRAL}]")

            lines += [
                f"",
                f"  [bold {ACCENT}]── Results ───────────────────────────────────────────────[/bold {ACCENT}]",
                f"  NPV = Σ PV(CFs) - C₀",
                f"  [bold]NPV                    :  [bold {npv_colour}]{fmt_currency(npv)}[/bold {npv_colour}][/bold]",
                f"",
                f"  IRR: Rate where NPV = 0",
                f"  [bold]IRR                    :  [bold {irr_colour}]{fmt_pct(irr*100)}[/bold {irr_colour}][/bold]",
                f"  [bold]WACC (hurdle rate)     :  [{NEUTRAL}]{fmt_pct(wacc*100)}[/{NEUTRAL}][/bold]",
                f"  IRR vs WACC spread     :  [{irr_colour}]{fmt_pct((irr-wacc)*100)}[/{irr_colour}]",
                f"",
                f"  [bold]Investment Decision    :  {decision}[/bold]",
                f"  {'NPV > 0 and IRR > WACC → value-creating project' if npv > 0 and irr > wacc else 'NPV < 0 or IRR < WACC → destroys shareholder value'}",
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
            ]
            self.query_one("#npv-panel", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#npv-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")

    def _render_dividends(self, ticker, dividends, fin, price, peers):
        try:
            div_yield = fin.get("div_yield", 0)
            if div_yield and div_yield > 1:
                div_yield_pct = div_yield
            else:
                div_yield_pct = div_yield * 100 if div_yield else 0

            lines = [
                f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]DIVIDEND ANALYSIS — {ticker}[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*66}[/bold {ACCENT}]",
                f"",
                f"  [bold]Current Price         :[/bold]  {fmt_currency(price)}",
                f"  [bold]Dividend Yield (TTM)  :[/bold]  [{POSITIVE if div_yield_pct > 0 else DIM}]{fmt_pct(div_yield_pct)}[/{POSITIVE if div_yield_pct > 0 else DIM}]",
                f"  [bold]EPS (TTM)             :[/bold]  {fmt_currency(fin.get('eps_ttm', 0))}",
                f"",
            ]

            if dividends:
                lines += [
                    f"  [bold {ACCENT}]── Dividend History ──────────────────────────────────────[/bold {ACCENT}]",
                    f"  {'Ex-Date':>12}  {'Amount':>12}  {'Currency':>8}",
                    f"  {'─'*12}  {'─'*12}  {'─'*8}",
                ]
                for d in dividends[:10]:
                    lines.append(f"  {str(d.get('ex_date','')):>12}  [{POSITIVE}]{fmt_currency(d.get('amount',0)):>12}[/{POSITIVE}]  {d.get('currency','USD'):>8}")

                # Annual dividend total
                if len(dividends) >= 4:
                    annual_div = sum(d.get("amount", 0) for d in dividends[:4])
                    payout = annual_div / fin.get("eps_ttm", 1) * 100 if fin.get("eps_ttm") else 0
                    lines += [
                        f"",
                        f"  Annual Dividend (last 4 payments) : [{POSITIVE}]{fmt_currency(annual_div)}[/{POSITIVE}]",
                        f"  Payout Ratio (est.)               : [{NEUTRAL}]{fmt_pct(payout)}[/{NEUTRAL}]",
                    ]
            else:
                lines.append(f"  [{DIM}]No dividend history found (may be a non-dividend stock)[/{DIM}]")

            if peers:
                lines += [
                    f"",
                    f"  [bold {ACCENT}]── Peer Comparison ───────────────────────────────────────[/bold {ACCENT}]",
                    f"  Peers (sector): {', '.join(peers[:6])}",
                    f"  [{DIM}](Connect peers to compare dividend yields in detail)[/{DIM}]",
                ]

            lines.append(f"[bold {ACCENT}]{'═'*66}[/bold {ACCENT}]")
            self.query_one("#div-panel", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#div-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")

    def _render_sensitivity(self, ticker, valuation):
        if not valuation:
            self.query_one("#sens-panel", Static).update(f"[{DIM}]Run valuation first.[/{DIM}]")
            return
        try:
            sens   = valuation.get("sensitivity", [])
            wacc   = valuation.get("wacc", 0)
            price  = valuation.get("market_price", 0)
            iv     = valuation.get("intrinsic_value", 0)

            lines = [
                f"[bold {ACCENT}]{'═'*72}[/bold {ACCENT}]",
                f"  [bold {ACCENT}]SENSITIVITY ANALYSIS — Intrinsic Value vs WACC ({ticker})[/bold {ACCENT}]",
                f"[bold {ACCENT}]{'─'*72}[/bold {ACCENT}]",
                f"",
                f"  Market Price: [bold white]{fmt_currency(price)}[/bold white]   Base WACC: [{NEUTRAL}]{fmt_pct(wacc*100)}[/{NEUTRAL}]   Base IV: [{ACCENT}]{fmt_currency(iv)}[/{ACCENT}]",
                f"",
                f"  {'WACC':>8}  {'Intrinsic Value':>16}  {'vs Market':>12}  Visual",
                f"  {'─'*8}  {'─'*16}  {'─'*12}  {'─'*35}",
            ]

            for item in sens:
                w    = item["wacc"]
                iv_w = item["intrinsic"]
                diff = ((iv_w - price) / price * 100) if price else 0
                diff_colour = POSITIVE if diff > 0 else NEGATIVE
                marker = " ◄ BASE" if abs(w - wacc) < 0.005 else ""
                bar_len = min(int(abs(diff) / 3), 30)
                bar = ("█" * bar_len)
                bar_str = f"[{diff_colour}]{bar}[/{diff_colour}]"
                lines.append(
                    f"  [{NEUTRAL}]{fmt_pct(w*100):>8}[/{NEUTRAL}]  "
                    f"[bold {ACCENT}]{fmt_currency(iv_w):>16}[/bold {ACCENT}]  "
                    f"[{diff_colour}]{fmt_pct(diff):>12}[/{diff_colour}]  "
                    f"{bar_str}[bold yellow]{marker}[/bold yellow]"
                )

            lines += [
                f"",
                f"  [bold {ACCENT}]── Interpretation ───────────────────────────────────────────────[/bold {ACCENT}]",
                f"  A higher WACC lowers intrinsic value (riskier discount rate).",
                f"  Rows where IV > Market Price suggest undervaluation at that WACC.",
                f"[bold {ACCENT}]{'═'*72}[/bold {ACCENT}]",
            ]
            self.query_one("#sens-panel", Static).update("\n".join(lines))
        except Exception as e:
            self.query_one("#sens-panel", Static).update(f"[{NEGATIVE}]Render error: {e}[/{NEGATIVE}]")


# ── App ────────────────────────────────────────────────────────────────────────

class ValuationApp(App):
    TITLE   = "📊 Company Valuation & Investment Dashboard"
    CSS_PATH = None

    CSS = """
    App {
        background: $background;
    }
    Header {
        background: $accent;
        color: $background;
        text-style: bold;
    }
    Footer {
        background: $surface;
    }
    """

    SCREENS = {"dashboard": DashboardScreen}

    def on_mount(self) -> None:
        self.push_screen(DashboardScreen())


def main():
    # Check for .env
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print("⚠️  No .env file found. Creating template...")
        env_path.write_text(
            "ALPACA_API_KEY=your_alpaca_api_key_here\n"
            "ALPACA_SECRET_KEY=your_alpaca_secret_key_here\n"
            "FINNHUB_API_KEY=your_finnhub_api_key_here\n"
        )
        print(f"✅ Created {env_path}")
        print("   Please edit it with your actual API keys, then re-run.")
        sys.exit(0)

    ok, err = df.validate_keys()
    if not ok:
        print(f"⚠️  API key warning: {err}")
        print("   Some features may not work. Edit .env to fix.")

    app = ValuationApp()
    app.run()


if __name__ == "__main__":
    main()