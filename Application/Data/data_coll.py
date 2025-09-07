import os
import pandas as pd
from nsepython import nsefetch


def get_historical_data(symbol: str,index_type:str, series: str, start_date: str, end_date: str, save_folder: str):

    # NSE API for historical data
    url_equity = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22{series}%22]&from={start_date}&to={end_date}"
    url_indices = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}"

    # Fetch data
    if series == "EQ":
        url = url_equity
    else:
        url = url_indices
    data = nsefetch(url)

    # Safe check for 'data' field before creating DataFrame
    if isinstance(data, dict) and 'data' in data:
        df = pd.DataFrame(data['data'])
    else:
        print(f"No 'data' field in response for symbol: {symbol}, series: {series}.")
        return

    if df.empty:
        print("No data found. Please check symbol, series, or date range.")
        return

    # Select useful columns
    df = df[['CH_TIMESTAMP','CH_OPENING_PRICE','CH_TRADE_HIGH_PRICE',
             'CH_TRADE_LOW_PRICE','CH_CLOSING_PRICE','CH_TOT_TRADED_QTY']]

    # Rename columns
    df.columns = ['Date','Open','High','Low','Close','Volume']

    # Ensure folder exists
    os.makedirs(save_folder, exist_ok=True)

    # File path
    file_path = os.path.join(save_folder, f"{symbol}_history.parquet")

    # Save as parquet
    df.to_parquet(file_path, index=False)
    print(f"Data saved successfully at: {file_path}")





df = pd.read_parquet("/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/top50_indian_stocks.parquet", engine="pyarrow")
symbols = df["Symbol"].tolist()
for symbol in symbols:
    series = "EQ"
    start_date = "01-01-2025"
    end_date = "31-03-2025"
    save_folder = "/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/Assets Data"   # Change this folder name if needed

    get_historical_data(symbol, "", series, start_date, end_date, save_folder)