import numpy as np
import pandas as pd

def cross(series_a, series_b):
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
    """ data must contain columns titled 'open', 'close', 'high', 'low'
    """
    ha_open = pd.Series(index=data.index)
    ha_close = pd.Series(index=data.index)
    ha_high = pd.Series(index=data.index)
    ha_low = pd.Series(index=data.index)

    prev_bar_mid = None

    for index, row in data.iterrows():
        ha_close.iloc[index] = 0.25 * (row['open'] + row['close'] + row['high'] + row['low'])
        if prev_bar_mid == None:
            ha_open.iloc[index] = ha_close.iloc[index]
        else:
            ha_open.iloc[index] = prev_bar_mid
        ha_high.iloc[index] = max(row['open'], row['high'], row['close'])
        ha_low.iloc[index] = min(row['open'], row['low'], row['close'])

        prev_bar_mid = 0.5 * (ha_close.iloc[index] + ha_open.iloc[index])

    return ha_open, ha_close, ha_high, ha_low

def log_mfi(data):
    result = pd.Series(index=data.index)
    for index, row in data.iterrows():
        
        if row['money_flow'] > 0:
            result.iloc[index] = np.log10(10 + abs(row['money_flow']))
        else:
            result.iloc[index] = 1
    return result
    