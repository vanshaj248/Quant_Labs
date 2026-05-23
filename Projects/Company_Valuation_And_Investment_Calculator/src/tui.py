"""
Interactive TUI for company data exploration and valuation
Built with textual framework - Complete rewrite
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, Label, DataTable
from textual.binding import Binding
from textual.screen import Screen
import pandas as pd

from src.database.company_db import CompanyDatabase
from src.ingestion.ingestion import DataIngestionPipeline


class CompanyListScreen(Screen):
    """Screen to select a company."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("enter", "select_company", "Select"),
    ]
    
    def __init__(self):
        super().__init__()
        self.companies = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
            "META", "TSLA", "BRK.B", "JPM", "V"
        ]
    
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            yield Label("📊 DCF Valuation Analyzer", id="title")
            yield Label("Select a company to analyze:", id="subtitle")
            yield DataTable(id="company_list")
            with Horizontal(id="button_row"):
                yield Button("View Data", id="view_btn", variant="primary")
                yield Button("Ingest", id="ingest_btn")
                yield Button("Quit", id="quit_btn", variant="error")
        yield Footer()
    
    def on_mount(self):
        """Populate company list."""
        table = self.query_one("#company_list", DataTable)
        table.add_column("Ticker", key="ticker", width=10)
        table.add_column("Status", key="status", width=15)
        table.add_column("Price", key="price", width=15)
        
        for ticker in self.companies:
            db = CompanyDatabase(ticker)
            price = db.get_current_price()
            status = "✓ Data" if price else "○ Empty"
            table.add_row(ticker, status, f"${price:.2f}" if price else "N/A")
            db.close()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        table = self.query_one("#company_list", DataTable)
        
        if event.button.id == "view_btn":
            self.action_select_company()
        elif event.button.id == "ingest_btn":
            if table.cursor_row is not None:
                row = table.get_row_at(table.cursor_row)
                self.app.push_screen(IngestionScreen(str(row[0])))
        elif event.button.id == "quit_btn":
            self.app.exit()
    
    def action_select_company(self):
        """Select the current company."""
        table = self.query_one("#company_list", DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            self.app.push_screen(CompanyDataScreen(str(row[0])))
    
    def action_quit(self):
        self.app.exit()


class IngestionScreen(Screen):
    """Screen to ingest data for a company."""
    
    BINDINGS = [
        Binding("q", "back", "Back"),
    ]
    
    def __init__(self, ticker: str):
        super().__init__()
        self.ticker = ticker
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label(f"📥 Ingesting Data for {self.ticker}", id="title")
            yield Static("", id="log_display")
            with Horizontal():
                yield Button("Back", id="back_btn", variant="primary")
        yield Footer()
    
    def on_mount(self):
        """Run ingestion."""
        log = self.query_one("#log_display", Static)
        log.update(f"Ingesting {self.ticker}...\n\n")
        
        try:
            pipeline = DataIngestionPipeline()
            pipeline.ingest_company(self.ticker, fetch_market=True, fetch_financials=True)
            log.update(f"✓ Ingestion of {self.ticker} complete!")
        except Exception as e:
            log.update(f"❌ Error: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()
    
    def action_back(self):
        self.app.pop_screen()


class CompanyDataScreen(Screen):
    """Screen displaying company data."""
    
    BINDINGS = [
        Binding("q", "back", "Back"),
    ]
    
    def __init__(self, ticker: str):
        super().__init__()
        self.ticker = ticker
        self.db = CompanyDatabase(ticker)
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label(f"📈 {self.ticker} - Data", id="title")
            
            # Market data
            with Vertical(id="market_section"):
                yield Label("Latest Quote:", id="quote_label")
                yield DataTable(id="market_table")
            
            # Financials
            with Vertical(id="financials_section"):
                yield Label("Financials (Annual):", id="fin_label")
                yield DataTable(id="financials_table")
            
            # Buttons
            with Horizontal():
                yield Button("Back", id="back_btn", variant="primary")
        yield Footer()
    
    def on_mount(self):
        """Load data."""
        self.load_market_data()
        self.load_financials()
    
    def load_market_data(self):
        """Load market data."""
        table = self.query_one("#market_table", DataTable)
        table.add_column("Metric", key="metric")
        table.add_column("Value", key="value")
        
        try:
            df = self.db.get_market_data(limit=1)
            if not df.empty:
                row = df.iloc[-1]
                table.add_row("Timestamp", str(row['timestamp'])[:10])
                table.add_row("Open", f"${row['open']:.2f}")
                table.add_row("High", f"${row['high']:.2f}")
                table.add_row("Low", f"${row['low']:.2f}")
                table.add_row("Close", f"${row['close']:.2f}")
                table.add_row("Volume", f"{int(row['volume']):,}")
        except Exception as e:
            self.query_one("#quote_label").update(f"Error: {e}")
    
    def load_financials(self):
        """Load financials."""
        table = self.query_one("#financials_table", DataTable)
        table.add_column("Year", key="year", width=10)
        table.add_column("Revenue (B)", key="rev", width=15)
        table.add_column("Net Income (B)", key="ni", width=15)
        table.add_column("FCF (B)", key="fcf", width=15)
        
        try:
            df = self.db.get_latest_financials(years=5)
            if not df.empty:
                for _, row in df.iterrows():
                    table.add_row(
                        str(int(row['fiscal_year'])),
                        f"${row['revenue']/1e9:.1f}" if row['revenue'] else "N/A",
                        f"${row['net_income']/1e9:.1f}" if row['net_income'] else "N/A",
                        f"${row['free_cash_flow']/1e9:.1f}" if row['free_cash_flow'] else "N/A"
                    )
        except Exception as e:
            self.query_one("#fin_label").update(f"Error: {e}")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back_btn":
            self.app.pop_screen()
            self.db.close()
    
    def action_back(self):
        self.app.pop_screen()
        self.db.close()


class ValuationApp(App):
    """Main TUI application."""
    
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }
    
    Container {
        margin: 1 2;
        border: solid $primary;
        padding: 1;
    }
    
    #title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    
    #subtitle {
        color: $text-muted;
        margin-bottom: 1;
    }
    
    #button_row {
        height: 3;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
    }
    
    DataTable {
        height: auto;
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def on_mount(self):
        self.title = "DCF Valuation Analyzer"
        self.push_screen(CompanyListScreen())


def run_tui():
    """Launch the TUI."""
    app = ValuationApp()
    app.run()


if __name__ == "__main__":
    run_tui()
