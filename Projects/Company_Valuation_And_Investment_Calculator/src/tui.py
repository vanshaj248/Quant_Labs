"""
DCF Valuation TUI Application
Interactive terminal interface for company valuation analysis
"""

from textual.app import App, ComposeResult, on
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Select, DataTable, Label, Input
from textual.screen import Screen
from textual.binding import Binding
from src.database.init_db import CompanyDatabase, init_default_companies
from src.valuation.dcf import DCFCalculator, DCFValuation
from src.valuation.wacc import WACCCalculator
from src.ingestion.ingestion import FinancialDataIngestion, load_api_key_from_env
from datetime import datetime


class CompanySelector(Screen):
    """Screen to select a company for valuation."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("enter", "select_company", "Select"),
    ]
    
    def __init__(self):
        super().__init__()
        self.db = CompanyDatabase()
        self.selected_ticker = None
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label("📊 DCF Valuation Analysis")
            yield Label("Select a company to analyze:")
            
            # Get companies from database
            companies = self.db.get_all_companies()
            company_options = [(str(c[0]), str(c[0])) for c in companies]
            
            if not company_options:
                yield Label("⚠️ No companies in database. Initializing...")
                init_default_companies()
                companies = self.db.get_all_companies()
                company_options = [(str(c[0]), str(c[0])) for c in companies]
            
            yield Select(
                company_options,
                id="company_select",
                prompt="Choose a company:"
            )
            
            with Horizontal():
                yield Button("Analyze", id="analyze_btn", variant="primary")
                yield Button("Ingest Data", id="ingest_btn")
                yield Button("Quit", id="quit_btn")
        
        yield Footer()
    
    @on(Button.Pressed, "#analyze_btn")
    def on_analyze(self):
        """Handle analyze button press."""
        select = self.query_one("#company_select", Select)
        if select.value != Select.BLANK:
            self.selected_ticker = select.value
            self.app.push_screen(ValuationScreen(self.selected_ticker))
    
    @on(Button.Pressed, "#ingest_btn")
    def on_ingest(self):
        """Handle data ingestion."""
        api_key = load_api_key_from_env()
        if not api_key:
            self.notify("❌ API key not found in .env", timeout=3)
            return
        
        ingestion = FinancialDataIngestion(api_key)
        companies = ["AAPL", "MSFT", "GOOGL"]
        ingestion.ingest_multiple(companies)
        ingestion.close()
        self.notify("✓ Data ingestion complete", timeout=3)
    
    @on(Button.Pressed, "#quit_btn")
    def on_quit(self):
        """Quit application."""
        self.app.exit()
    
    def action_quit(self):
        self.app.exit()
    
    def action_select_company(self):
        self.on_analyze()


class ValuationScreen(Screen):
    """Screen displaying DCF valuation for selected company."""
    
    BINDINGS = [
        Binding("q", "back", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, ticker: str):
        super().__init__()
        self.ticker = ticker.upper()
        self.db = CompanyDatabase()
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Container():
            yield Label(f"📈 DCF Valuation - {self.ticker}")
            
            # Valuation summary
            with Vertical(id="valuation_summary"):
                yield Label("Loading valuation data...")
            
            # Key metrics table
            with Vertical(id="metrics_table"):
                yield Label("Financial Metrics:")
                yield DataTable(id="metrics_table_widget")
            
            # DCF breakdown
            with Vertical(id="dcf_breakdown"):
                yield Label("DCF Calculation Breakdown:")
                yield DataTable(id="dcf_table_widget")
            
            with Horizontal():
                yield Button("Sensitivity Analysis", id="sensitivity_btn")
                yield Button("Export Report", id="export_btn")
                yield Button("Back", id="back_btn", variant="primary")
        
        yield Footer()
    
    def on_mount(self):
        """Load and display valuation data."""
        self.load_valuation_data()
    
    def load_valuation_data(self):
        """Load valuation from database or calculate."""
        valuation = self.db.get_latest_valuation(self.ticker)
        
        if valuation:
            self.display_valuation(valuation)
        else:
            self.notify(f"No valuation found for {self.ticker}. Run ingestion first.", timeout=5)
    
    def display_valuation(self, valuation):
        """Display valuation results."""
        try:
            summary_widget = self.query_one("#valuation_summary", Vertical)
            summary_widget.children = [
                Label(f"{'='*60}"),
                Label(f"Current Price: ${valuation[2]:.2f}" if valuation[2] else "N/A"),
                Label(f"Intrinsic Value: ${valuation[17]:.2f}" if valuation[17] else "N/A"),
                Label(f"Margin of Safety: {valuation[18]*100:.1f}%" if valuation[18] else "N/A"),
                Label(f"Recommendation: {valuation[19]}" if valuation[19] else "HOLD"),
                Label(f"{'='*60}"),
            ]
        except Exception as e:
            self.notify(f"Error displaying valuation: {e}", timeout=3)
    
    @on(Button.Pressed, "#back_btn")
    def on_back(self):
        """Go back to company selector."""
        self.app.pop_screen()
    
    def action_back(self):
        self.on_back()
    
    def action_refresh(self):
        self.load_valuation_data()


class DCFValuationApp(App):
    """Main application class."""
    
    CSS = """
    Screen {
        layout: vertical;
        background: $surface;
    }
    
    Container {
        margin: 1 2;
        border: solid $accent;
        padding: 1;
    }
    
    Label {
        margin: 0 1;
        color: $text;
    }
    
    Select {
        margin: 1 0;
    }
    
    Button {
        margin: 0 1;
    }
    
    DataTable {
        height: auto;
        margin: 1 0;
    }
    
    #valuation_summary {
        border: solid $primary;
        padding: 1;
        margin: 1 0;
        background: $boost;
    }
    
    #metrics_table {
        margin: 1 0;
    }
    
    #dcf_breakdown {
        margin: 1 0;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield CompanySelector()

    def on_mount(self):
        """Initialize application."""
        self.title = "DCF Valuation Analyzer"


def run_tui():
    """Run the TUI application."""
    app = DCFValuationApp()
    app.run()


if __name__ == "__main__":
    run_tui()
