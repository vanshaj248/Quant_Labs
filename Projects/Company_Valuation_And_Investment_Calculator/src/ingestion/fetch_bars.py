from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from src.database.connection import get_connection
from src.api.client import client

conn = get_connection()

request = StockBarsRequest(
    symbol_or_symbols=["AAPL"],
    timeframe=TimeFrame.Day,
    start="2023-01-01"
)

bars = client.get_stock_bars(request)

df = bars.df.reset_index()

print(df.head())

conn.execute("""
CREATE TABLE IF NOT EXISTS stock_prices AS
SELECT * FROM df LIMIT 0
""")

conn.execute("""
INSERT INTO stock_prices
SELECT * FROM df
""")

print("Data inserted successfully!")
