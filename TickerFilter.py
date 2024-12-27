import yfinance as yf
import pandas as pd
import json

with open("Data/config.json", "r") as file:
    config = json.load(file)
min_market_cap = config["min_market_cap"]

nifty500list = pd.read_csv('Data/Nifty500 Data.csv')
nifty500_symbols = nifty500list.iloc[:, 2].tolist()

filtered_tickers = []
for ticker in nifty500_symbols:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if info.get("marketCap", 0) >= min_market_cap:
            filtered_tickers.append(ticker)
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")


filtered_csv = pd.DataFrame(filtered_tickers, columns=['ticker'])
filtered_csv.to_csv("Data/Filtered_Tickers.csv", index=False)


