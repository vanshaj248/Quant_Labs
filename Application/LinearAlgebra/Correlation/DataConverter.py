import pandas as pd

df = pd.read_csv("/Users/vanshaj/Work/GitHub/Novard-Labs/Testing/Correlation/combined_price_data.csv")

df.to_parquet("/Users/vanshaj/Work/GitHub/Novard-Labs/Testing/Correlation/CombinedPriceData.parquet", engine='pyarrow')