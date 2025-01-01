import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json


def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetch historical stock data and calculate moving averages.
    """
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    stock_data['7_day_MA'] = stock_data['Close'].rolling(window=7).mean()
    stock_data['21_day_MA'] = stock_data['Close'].rolling(window=21).mean()
    return stock_data

def identify_golden_cross(stock_data):
    """
    Identify golden cross in the stock data.
    """
    golden_cross_dates = []
    for i in range(1, len(stock_data)):
        if stock_data['7_day_MA'].iloc[i] > stock_data['21_day_MA'].iloc[i] and \
           stock_data['7_day_MA'].iloc[i-1] <= stock_data['21_day_MA'].iloc[i-1]:
            golden_cross_dates.append(stock_data.index[i])
    return golden_cross_dates

def fetch_additional_info(ticker):
    """
    Fetch additional company info.
    """
    stock = yf.Ticker(ticker)
    info = stock.info
    return {
        'Market Cap (crores)': (info.get('marketCap', 'N/A'))/10000000,
        'Share Price (rupees)': info.get('currentPrice', 'N/A'),
        'Company Name': info.get('shortName', 'N/A')
    }

def golden_cross_scanner(min_market_cap, lookback_days):
    """
    Scan for golden cross in dynamically fetched tickers.
    """
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=lookback_days + 21)).strftime('%Y-%m-%d')

    filtered_ticker_csv = pd.read_csv("Data/Filtered_Tickers.csv")
    tickers = filtered_ticker_csv['ticker'].tolist()

    results = []
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        try:
            stock_data = fetch_stock_data(ticker, start_date, end_date)
            golden_cross_dates = identify_golden_cross(stock_data)
            
            for date in golden_cross_dates:
                if date >= datetime.today() - timedelta(days=lookback_days):
                    info = fetch_additional_info(ticker)
                    results.append({
                        'Ticker': ticker,
                        'Company Name': info['Company Name'],
                        'Market Cap (crores)': info['Market Cap (crores)'],
                        'Share Price (rupees)': info['Share Price (rupees)'],
                        'Golden Cross Date': date.strftime('%Y-%m-%d')
                    })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
    
    return pd.DataFrame(results)


with open("Data/config.json", "r") as file:
    config = json.load(file)

lookback_days = config["lookback_days"]
min_market_cap = config["min_market_cap"]

# Run the scanner
goldencrosses = golden_cross_scanner(min_market_cap, lookback_days)
if not goldencrosses.empty:
    results = goldencrosses.drop(goldencrosses.columns[0], axis=1)
else:
    results = goldencrosses

results.to_csv('Data/golden_cross_results.csv', index=False)
