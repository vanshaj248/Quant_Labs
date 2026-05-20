from alpaca.data.live import StockDataStream
from src.api.client import API_KEY, SECRET_KEY

stream = StockDataStream(API_KEY,SECRET_KEY)
stream.subscribe_trades(trade_handler, "AAPL")
async def trade_handler(data):

    print(data)