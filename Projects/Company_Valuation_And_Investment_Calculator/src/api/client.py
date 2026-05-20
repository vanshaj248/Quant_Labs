from alpaca.data.historical import StockHistoricalDataClient
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY")

client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
