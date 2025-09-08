import os
import pandas as pd
from nsepython import nsefetch

def get_historical_data(symbol: str,index_type:str, series: str, start_date: str, end_date: str, save_folder: str):

    # NSE API for historical data
    url_equity = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22{series}%22]&from={start_date}&to={end_date}"
    url_indices = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index_type}&from={start_date}&to={end_date}"

    # Fetch data
    if series=="EQ":
        url = url_equity
    else:
        url = url_indices
    data = nsefetch(url)

    if series=="EQ":
        df = pd.DataFrame(data['data'])
    else:
        df_turnover = pd.DataFrame(data['data'].get('indexTurnoverRecords', []))
        df_close = pd.DataFrame(data['data'].get('indexCloseOnlineRecords', []))


    if (series == "EQ" and df.empty) or (series != "EQ" and (df_turnover.empty or df_close.empty)):
        print("No data found. Please check symbol, series, or date range.")
        return

    # Select useful columns
    if series=="EQ":
        df = df[['CH_TIMESTAMP','CH_OPENING_PRICE','CH_TRADE_HIGH_PRICE',
                'CH_TRADE_LOW_PRICE','CH_CLOSING_PRICE','CH_TOT_TRADED_QTY']]
    elif series=="":
        df = pd.concat([df_turnover, df_close], axis=1)
        df = df[['EOD_TIMESTAMP', 'EOD_OPEN_INDEX_VAL', 'EOD_HIGH_INDEX_VAL',
             'EOD_LOW_INDEX_VAL', 'EOD_CLOSE_INDEX_VAL', 'HIT_TRADED_QTY']] 


    # Rename columns
    df.columns = ['Date','Open','High','Low','Close','Volume']

    # Ensure folder exists
    os.makedirs(save_folder, exist_ok=True)

    # File path
    if series == "EQ":
        file_path = os.path.join(save_folder, f"{symbol}_history.parquet")
    else:
        file_path = os.path.join(save_folder, f"{index_type}_history.parquet")

    # Save as parquet
    df.to_parquet(file_path, index=False)
    print(f"Data saved successfully at: {file_path}")




