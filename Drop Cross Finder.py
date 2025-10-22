import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


def fetch_stock_data(all_data, ticker):
    stock_data = all_data[ticker].copy()
    stock_data['7_day_MA'] = stock_data['Close'].rolling(window=7).mean()
    stock_data['21_day_MA'] = stock_data['Close'].rolling(window=21).mean()
    return stock_data


def identify_golden_cross(stock_data):
    golden_cross_dates = []
    for i in range(1, len(stock_data)):
        if stock_data['7_day_MA'].iloc[i] < stock_data['21_day_MA'].iloc[i] and \
           stock_data['7_day_MA'].iloc[i-1] >= stock_data['21_day_MA'].iloc[i-1]:
            golden_cross_dates.append(stock_data.index[i])
    return golden_cross_dates


def fetch_additional_info(ticker, info_cache, lock):
    # Thread-safe cache
    with lock:
        if ticker not in info_cache:
            stock = yf.Ticker(ticker)
            info_cache[ticker] = stock.info
        info = info_cache[ticker]

    return {
        'Market Cap (crores)': (info.get('marketCap', 'N/A')) / 10000000 if info.get('marketCap') else 'N/A',
        'Share Price (rupees)': info.get('currentPrice', 'N/A'),
        'Company Name': info.get('shortName', 'N/A')
    }


def process_ticker(ticker, all_data, lookback_days, info_cache, lock):
    try:
        stock_data = fetch_stock_data(all_data, ticker)
        golden_cross_dates = identify_golden_cross(stock_data)

        recent_crosses = []
        for date in golden_cross_dates:
            if date >= datetime.today() - timedelta(days=lookback_days):
                info = fetch_additional_info(ticker, info_cache, lock)
                recent_crosses.append({
                    'Ticker': ticker,
                    'Company Name': info['Company Name'],
                    'Market Cap (crores)': info['Market Cap (crores)'],
                    'Share Price (rupees)': info['Share Price (rupees)'],
                    'Golden Cross Date': date.strftime('%Y-%m-%d')
                })
        return recent_crosses
    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return []


def golden_cross_scanner(min_market_cap, lookback_days):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=lookback_days + 21)).strftime('%Y-%m-%d')

    filtered_ticker_csv = pd.read_csv("Data/Filtered_Tickers.csv")
    tickers = filtered_ticker_csv['ticker'].tolist()

    print(f"Downloading all {len(tickers)} tickers in batch...")
    all_data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', auto_adjust=True)

    info_cache = {}
    lock = Lock()
    results = []

    # Use multithreading to process tickers faster
    print(f"Processing tickers in parallel...")
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = {executor.submit(process_ticker, t, all_data, lookback_days, info_cache, lock): t for t in tickers}
        for future in as_completed(futures):
            ticker_results = future.result()
            if ticker_results:
                results.extend(ticker_results)

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

results.to_csv('Data/drop_cross_results.csv', index=False)