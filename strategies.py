import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")


# Calculate Bollinger Bands
def calculate_bollinger_bands(data, window=20, num_std=2):
    data['SMA'] = data['close'].rolling(window).mean()
    data['Upper Band'] = data['SMA'] + (data['close'].rolling(window).std() * num_std)
    data['Lower Band'] = data['SMA'] - (data['close'].rolling(window).std() * num_std)


# Implementing the reversal trading strategy
def bollinger_bands_strategy(data):
    data['Position'] = 0  # 1 for buy, -1 for sell
    for i in range(len(data)):
        if data['close'].iloc[i] < data['Lower Band'].iloc[i]:
            data['Position'].iloc[i] = 1  # Buy signal
        elif data['close'].iloc[i] > data['Upper Band'].iloc[i]:
            data['Position'].iloc[i] = -1  # Sell signal

    # Calculate daily returns
    data['Daily Return'] = data['close'].pct_change()
    # Strategy returns: return when in position
    data['Strategy Return'] = data['Position'].shift(1) * data['Daily Return']

    # Calculate cumulative returns
    data['Cumulative Market Return'] = (1 + data['Daily Return']).cumprod()
    data['Cumulative Strategy Return'] = (1 + data['Strategy Return']).cumprod()



def plot_returns(data):
    # Plotting the results
    plt.figure(figsize=(14, 3))
    plt.plot(data['timestamp'], data['Cumulative Market Return'], label='Market Return', color='blue')
    plt.plot(data['timestamp'], data['Cumulative Strategy Return'], label='Strategy Return', color='orange')
    plt.title('Cumulative Returns: Market vs. Bollinger Bands Strategy')
    tickers = data[data.index %30==1]
    plt.xticks(tickers['timestamp'], rotation=50)

    plt.xlabel('timestamp')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid()
    plt.show()