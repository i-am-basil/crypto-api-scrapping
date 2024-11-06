import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import requests


def get_tickers():
    # Gets all tickers that are traded on binance
    url = 'https://api.binance.com/api/v3/exchangeInfo'

    # Send request to the API
    response = requests.get(url)

    # Check if the request was successful
    if response.ok:
        # Parse the JSON response
        data = response.json()

        # Extract the trading pairs
        trading_pairs = [item['symbol'] for item in data['symbols']]

        return trading_pairs
    else:
        print(f"Error {response.status_code}: Unable to fetch data from Binance API")
        return None

def get_prices(ticker, validation_dt='2024-05-26', interval='1d', limit=1000):
    url = 'https://api.binance.com/api/v3/klines'
    # Set the API parameters
    params = {
        'symbol': ticker,      # Trading pair symbol, e.g., 'BTCUSDT'
        'interval': interval,  # Candlestick interval
        'limit': limit,        # Number of data points
    }

    # Send request to the API
    response = requests.get(url, params=params)

    # Check if the request was successful
    if response.ok:
        # Parse the JSON response
        data = response.json()

        # Convert the response to a DataFrame with specified columns
        df = pd.DataFrame(
            data,
            columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'num_trades',
                'taker_buy_base_volume', 'taker_buy_quote_volume', 'ignore'
            ]
        )

        # Convert timestamp columns to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

        # Keep only the desired columns
        df = df[['timestamp', 'open', 'high', 'low', 'close']]
        df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype('float')
        if validation_dt:
            df = df.query(f'timestamp<"{validation_dt}"')
        return df
    else:
        print(f"Error {response.status_code}: Unable to fetch data from Binance API")
        return None


def calc_sortino(returns, risk_free_rate=0.0428):
    annual_return = calc_annual_return(returns)
    annual_excess_return = annual_return - risk_free_rate

    annual_downside_std = calc_annual_std(returns, 'downside')

    sortino_ratio = annual_excess_return / annual_downside_std
    # sortino_ratio = round(sortino_ratio.values[0], 3)
    if annual_downside_std == 0:
        return -float('inf')
    return round(sortino_ratio, 2)


def calc_annual_return(returns):
    returns = returns.values
    n = returns.shape[0]
    period_return = (returns[-1]/returns[0] - 1)[0]
    annual_return = (period_return) * (365 / n)
    return round(annual_return, 2)


def calc_annual_std(returns, type='downside'):
    rel_returns = returns.pct_change()\
                         .values[1:]

    if type == 'downside':
        rel_returns = rel_returns * (rel_returns < 0)

    std = np.std(rel_returns, ddof=1)
    annual_std = std * np.sqrt(365)
    return round(annual_std, 2)


def plot_prices(tickers):

    _, ax = plt.subplots(1,5,figsize=(16, 3))

    for k,ticker in enumerate(tickers):
        df = get_prices(ticker, interval='1d', limit=1000)
        ax[k].plot(df.index, df['close'], label=ticker)
        ax[k].legend(loc='best')
