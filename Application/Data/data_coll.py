import os
import pandas as pd
from nsepython import nsefetch
import yfinance as yf

def get_equity_historical_data(symbol: str, series: str, start_date: str, end_date: str, save_folder: str):

    # NSE API for historical equity data
    url_equity = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22{series}%22]&from={start_date}&to={end_date}"

    # Fetch data
    data = nsefetch(url_equity)

    df = pd.DataFrame(data['data'])

    if df.empty:
        print(f"No data found for symbol: {symbol}, series: {series}.")
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

def get_index_historical_data(index_type: str, start_date: str, end_date: str, save_folder: str):

    # NSE API for historical indices data
    url_indices = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}"

    # Fetch data
    data = nsefetch(url_indices)

    df_turnover = pd.DataFrame(data['data'].get('indexTurnoverRecords', []))
    df_close = pd.DataFrame(data['data'].get('indexCloseOnlineRecords', []))

    if df_turnover.empty or df_close.empty:
        print(f"No data found for index type: {index_type}.")
        return

    df = pd.concat([df_turnover, df_close], axis=1)
    df = df[['EOD_TIMESTAMP', 'EOD_OPEN_INDEX_VAL', 'EOD_HIGH_INDEX_VAL',
         'EOD_LOW_INDEX_VAL', 'EOD_CLOSE_INDEX_VAL', 'HIT_TRADED_QTY']]

    # Rename columns
    df.columns = ['Date','Open','High','Low','Close','Volume']

    # Ensure folder exists
    os.makedirs(save_folder, exist_ok=True)

    # File path
    file_path = os.path.join(save_folder, f"{index_type}_history.parquet")

    # Save as parquet
    df.to_parquet(file_path, index=False)
    print(f"Data saved successfully at: {file_path}")


def get_yahoo_finance_data_indices():
    df = pd.read_parquet("/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/US_indices.parquet", engine="pyarrow")
    symbols = df["Symbol"].tolist()
    index = df["indices"].tolist()

    for (symbol, indices) in zip(symbols, index):
        df = yf.download(symbol, start="2024-01-01", end="2025-01-01")
        data = pd.DataFrame(df)
        data.to_parquet(f"/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/Assets Data/INDICES/USA/{indices}_history.parquet", index=False)

    df = pd.read_parquet("/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/US50_equities.parquet", engine="pyarrow")
    symbols = df["Symbol"].tolist()
    equities = df["Equity"].tolist()

    for (symbol, equity) in zip(symbols, equities):
        df = yf.download(symbol, start="2024-01-01", end="2025-01-01")
        data = pd.DataFrame(df)
        data.to_parquet(f"/Users/vanshaj/Work/GitHub/Quant_Labs/Application/Data/Assets Data/EQUITY/USA/{equity}_history.parquet", index=False)