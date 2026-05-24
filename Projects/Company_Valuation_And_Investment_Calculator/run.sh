#!/usr/bin/env bash
# ─── Company Valuation Dashboard Launcher ─────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10+."
    exit 1
fi

# Install dependencies if needed
echo "🔍 Checking dependencies..."
pip install textual duckdb requests python-dotenv finnhub-python --break-system-packages -q 2>/dev/null || \
pip install textual duckdb requests python-dotenv finnhub-python -q

# Check .env
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << 'EOF'
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here
EOF
    echo "✅ Created .env — please fill in your API keys!"
    echo ""
    echo "   ALPACA:  https://alpaca.markets  (free account)"
    echo "   FINNHUB: https://finnhub.io      (free tier: 60 req/min)"
    echo ""
    read -p "Press Enter to open .env in your editor (or Ctrl+C to cancel)..."
    ${EDITOR:-nano} .env
fi

echo ""
echo "🚀 Starting Valuation Dashboard..."
echo ""
python3 main.py
