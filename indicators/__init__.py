import numpy as np
import pandas as pd

def cross(series_a, series_b):
    """ Returns a series of 1s and 0s.
        A 1 indicates that series_a has crossed over series_b,
        or that series_b has crossed over series_a
        in the current row. """
    result = pd.Series(index=series_a.index)
    prev_a, prev_b = series_a.iloc[0], series_b.iloc[0]

    for index, value in series_a.items():
        cur_a, cur_b = series_a.iloc[index], series_b.iloc[index]
        if np.isnan(prev_a) or np.isnan(prev_b) or np.isnan(cur_a) or np.isnan(cur_b):
            result.iloc[index] = 0
        elif prev_a > prev_b and cur_a > cur_b:
            result.iloc[index] = 0
        elif prev_a < prev_b and cur_a < cur_b:
            result.iloc[index] = 0
        else:
            result.iloc[index] = 1
        prev_a, prev_b = cur_a, cur_b
    return result

def crossunder(series_a, series_b):
    """ Returns a series of 1s and 0s.
        A 1 indicates that series_b has crossed over series_a
        in the current row. """
    result = pd.Series(index=series_a.index)
    prev_a, prev_b = series_a.iloc[0], series_b.iloc[0]

    for index, value in series_a.items():
        cur_a, cur_b = series_a.iloc[index], series_b.iloc[index]
        if np.isnan(prev_a) or np.isnan(prev_b) or np.isnan(cur_a) or np.isnan(cur_b):
            result.iloc[index] = 0
        elif prev_a > prev_b and cur_a < cur_b:
            result.iloc[index] = 1
        else:
            result.iloc[index] = 0
        prev_a, prev_b = cur_a, cur_b
    return result

def crossover(series_a, series_b):
    """ Returns a series of 1s and 0s.
        A 1 indicates that series_a has crossed over series_b
        in the current row. """
    result = pd.Series(index=series_a.index)
    prev_a, prev_b = series_a.iloc[0], series_b.iloc[0]

    for index, value in series_a.items():
        cur_a, cur_b = series_a.iloc[index], series_b.iloc[index]
        if np.isnan(prev_a) or np.isnan(prev_b) or np.isnan(cur_a) or np.isnan(cur_b):
            result.iloc[index] = 0
        elif prev_a < prev_b and cur_a > cur_b:
            result.iloc[index] = 1
        else:
            result.iloc[index] = 0
        prev_a, prev_b = cur_a, cur_b
    return result

def heiken_ashi(data):
    """ Assumes data contains columns titled 'open', 'close', 'high', 'low'.
        Returns four heiken ashi series: open, close, high and low. 
        
        1. The Heikin-Ashi Close is simply an average of the open, 
        high, low and close for the current period. 

        <b>HA-Close = (Open(0) + High(0) + Low(0) + Close(0)) / 4</b>

        2. The Heikin-Ashi Open is the average of the prior Heikin-Ashi 
        candlestick open plus the close of the prior Heikin-Ashi candlestick. 

        <b>HA-Open = (HA-Open(-1) + HA-Close(-1)) / 2</b> 

        3. The Heikin-Ashi High is the maximum of three data points: 
        the current period's high, the current Heikin-Ashi 
        candlestick open or the current Heikin-Ashi candlestick close. 

        <b>HA-High = Maximum of the High(0), HA-Open(0) or HA-Close(0) </b>

        4. The Heikin-Ashi low is the minimum of three data points: 
        the current period's low, the current Heikin-Ashi 
        candlestick open or the current Heikin-Ashi candlestick close.

        <b>HA-Low = Minimum of the Low(0), HA-Open(0) or HA-Close(0) </b>
        
        """
    ha_close = pd.Series(index=data.index)
    ha_open = pd.Series(index=data.index)
    ha_high = pd.Series(index=data.index)
    ha_low = pd.Series(index=data.index)

    for index, row in data.iterrows():
        if index:
            # create the first, artificial candle
            ha_close.iloc[index] = (row['open'] + row['close'] + row['high'] + row['low']) / 4.0
            ha_open.iloc[index] = (row['open'] + row['close']) / 2.0
            ha_high.iloc[index] = row['high']
            ha_low.iloc[index] = row['low']
        else:
            ha_close.iloc[index] = (row['open'] + row['close'] + row['high'] + row['low']) / 4.0
            ha_open.iloc[index] = (ha_open.iloc[index-1] + ha_close.iloc[index-1]) / 2.0
            ha_high.iloc[index] = max(row['high'], ha_close.iloc[index], ha_open.iloc[index])
            ha_low.iloc[index] = min(row['low'], ha_close.iloc[index], ha_open.iloc[index])

    return ha_open, ha_close, ha_high, ha_low

def log_mfi(data, side='short'):
    """ Assumes data contains a column titled 'money_flow'
        Returns series with log of the money flow. """
    result = pd.Series(index=data.index)
    if side == 'short':
        for index, row in data.iterrows():
            if row['money_flow'] > 0:
                result.iloc[index] = np.log10(10 + abs(row['money_flow']))
            else:
                result.iloc[index] = 1
    elif side == 'long':
        for index, row in data.iterrows():
            if row['money_flow'] < 0:
                result.iloc[index] = np.log10(10 + abs(row['money_flow']))
            else:
                result.iloc[index] = 1
    else:
        result = None
    return result        
    
def candle_value(data, ha=False):
    result = pd.Series(index=data.index)
    open_str = 'ha_open' if ha else 'open'
    close_str = 'ha_close' if ha else 'close'
    high_str = 'ha_high' if ha else 'high'
    low_str = 'ha_low' if ha else 'low'
    for index, row in data.iterrows():
        if (row[high_str] - row[low_str]) == 0:
            result.iloc[index] = 0.0
        else:
            result.iloc[index] = (row[close_str] - row[open_str]) / (row[high_str] - row[low_str])
    return result

def fractal_extrema(data, close):
    max_result = pd.Series(index=data.index)
    min_result = pd.Series(index=data.index)
    max_result.iloc[0] = 0
    max_result.iloc[1] = 0
    min_result.iloc[0] = 0
    min_result.iloc[1] = 0
    for index in range(2, len(data)-2):
        # fractal maxima
        if data.at[index-2, close] < data.at[index-1, close] < data.at[index, close] > data.at[index+1, close] > data.at[index+2, close]:
            max_result.iloc[index] = 1
        else:
            max_result.iloc[index] = 0
        #fractal minima
        if data.at[index-2, close] > data.at[index-1, close] > data.at[index, close] < data.at[index+1, close] < data.at[index+2, close]:
            min_result.iloc[index] = 1
        else:
            min_result.iloc[index] = 0
    return max_result, min_result

def fractal_sum(data, fractal_close, original_close, num):
    num_result = pd.Series(index=data.index)
    sum_result = pd.Series(index=data.index)
    for i in range(0, num):
        num_result.iloc[i] = np.NaN
        sum_result.iloc[i] = np.NaN
    for j in range(num, len(data)):
        num_fractals = 0
        sum_fractals = 0
        for k in range(j-num, j):
            if data.at[k, fractal_close] == 1:
                num_fractals += 1
                sum_fractals += data.at[k, original_close]
        num_result.iloc[j] = num_fractals
        sum_result.iloc[j] = sum_fractals
    return num_result, sum_result