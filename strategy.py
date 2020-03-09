import pandas as pd
import numpy as np
import ta
from actions import Action


### Old

""" WT_OVERBOUGHT_1 = 53
WT_OVERBOUGHT_2 = 60
WT_OVERSOLD_1 = -53
WT_OVERSOLD_2 = -60

EMA_0_PERIOD = 5
EMA_1_PERIOD = 11
EMA_2_PERIOD = 15
EMA_3_PERIOD = 18
EMA_4_PERIOD = 21
EMA_5_PERIOD = 25
EMA_6_PERIOD = 29
EMA_7_PERIOD = 33

RSI_PERIOD = 14

WT_CHANNEL_LENGTH = 7
WT_AVERAGE_LENGTH = 12 """

### New

CHANNEL_LENGTH = 9
AVERAGE_LENGTH = 12
OVER_BOUGHT_1 = 60
OVER_BOUGHT_2 = 53
OVER_SOLD_1 = -60
OVER_SOLD_2 = -53
OVER_SOLD_3 = -100

SMOOTH_KW = 3
SMOOTH_DW = 3
LENGTH_RSI_W = 14
LENGTH_STOCH_W = 14
USE_LOG_W = True

RSI_MFI_PERIOD = 60
RSI_MFI_MULT = 190

class Strategy:
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
        Must call Strategy.load_klines before using Strategy.get_action
    """
    def __init__(self):
        print('initialising new strategy')
        

    def load_klines(self, data):
        self.df = pd.DataFrame.from_dict(data)
        
        self.df['interval'] = pd.to_numeric(self.df['interval'])
        self.df['open_time'] = pd.to_numeric(self.df['open_time'])
        self.df['open'] = pd.to_numeric(self.df['open'])
        self.df['high'] = pd.to_numeric(self.df['high'])
        self.df['low'] = pd.to_numeric(self.df['low'])
        self.df['close'] = pd.to_numeric(self.df['close'])
        self.df['volume'] = pd.to_numeric(self.df['volume'])
        self.df['turnover'] = pd.to_numeric(self.df['turnover'])

        self._add_indicators()
        self._add_logic()

    def _cross(self, series_a, series_b):
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

    def _crossunder(self, series_a, series_b):
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

    def _crossover(self, series_a, series_b):
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

    def _fractal_top(self, series):
        """ return series of 1s and 0s and NaNs
            the 1 is where the kline is fractal top, 0 not, NaN = not enough surrounding klines
        """
        if len(series) < 5: # need at least 5 to declare a top
            return pd.Series(data=np.zeros(len(series)), index=series.index)
        
        result = pd.Series(index=series.index)

        for x in range(2, len(series) - 2):
            result.iloc[x+2] = (1 if (series.iloc[x-2] < series.iloc[x] and series.iloc[x-1] < series.iloc[x] and series.iloc[x] > series.iloc[x+1] and series.iloc[x] > series.iloc[x+2]) else 0)
        
        print(result)
        return result

    def _fractal_bottom(self, series):
        """ return series of 1s and 0s and NaNs
            the 1 is where the kline is fractal top, 0 not, NaN = not enough surrounding klines
        """
        if len(series) < 5: # need at least 5 to declare a top
            return pd.Series(data=np.zeros(len(series)), index=series.index)
        
        result = pd.Series(index=series.index)

        for x in range(2, len(series) - 2):
            result.iloc[x+2] = (1 if (series.iloc[x-2] > series.iloc[x] and series.iloc[x-1] > series.iloc[x] and series.iloc[x] < series.iloc[x+1] and series.iloc[x] < series.iloc[x+2]) else 0)
        
        return result

    def _value_when(self, source_col, desired_val, desired_col, n, offset=0):
        """ returns the value of self.df[desired_col] at the
            nth most recent index where self.df[source_col] == desired_val
        """
        mask = self.df[source_col].isin([desired_val])
        tmp_df = self.df[mask]
        return tmp_df.tail(n+1)[desired_col].head().iloc[0] # this is the opposite of maintainable, sorry

    def _add_ha_data(self):
        ha_open = pd.Series(index=self.df.index)
        ha_close = pd.Series(index=self.df.index)
        ha_high = pd.Series(index=self.df.index)
        ha_low = pd.Series(index=self.df.index)

        prev_bar_mid = None

        for index, row in self.df.iterrows():
            ha_close.iloc[index] = 0.25 * (row['open'] + row['close'] + row['high'] + row['low'])
            if prev_bar_mid == None:
                ha_open.iloc[index] = ha_close.iloc[index]
            else:
                ha_open.iloc[index] = prev_bar_mid
            ha_high.iloc[index] = max(row['open'], row['high'], row['close'])
            ha_low.iloc[index] = min(row['open'], row['low'], row['close'])

            prev_bar_mid = 0.5 * (ha_close.iloc[index] + ha_open.iloc[index])

        self.df['ha_open'] = ha_open
        self.df['ha_close'] = ha_close
        self.df['ha_high'] = ha_high
        self.df['ha_low'] = ha_low

    def _add_indicators(self):
        """ Define the indicators to be used by your strategy in this function.
        """

        """ # Market Cipher A Indicators
        # EMAs
        ema_0 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_0_PERIOD, fillna=True)
        ema_1 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_1_PERIOD, fillna=True)
        ema_2 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_2_PERIOD, fillna=True)
        ema_3 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_3_PERIOD, fillna=True)
        ema_4 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_4_PERIOD, fillna=True)
        ema_5 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_5_PERIOD, fillna=True)
        ema_6 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_6_PERIOD, fillna=True)
        ema_7 = ta.trend.EMAIndicator(close=self.df['close'], n=EMA_7_PERIOD, fillna=True)
        
        self.df['ema_0'] = ema_0.ema_indicator()
        self.df['ema_1'] = ema_1.ema_indicator()
        self.df['ema_2'] = ema_2.ema_indicator()
        self.df['ema_3'] = ema_3.ema_indicator()
        self.df['ema_4'] = ema_4.ema_indicator()
        self.df['ema_5'] = ema_5.ema_indicator()
        self.df['ema_6'] = ema_6.ema_indicator()
        self.df['ema_7'] = ema_7.ema_indicator()

        # RSI
        rsi = ta.momentum.rsi(close=self.df['close'], n=RSI_PERIOD, fillna=True)
        self.df['rsi'] = rsi

        # Wavetrend
        #self.df['ohcl4'] = self.df[['open', 'high', 'low', 'close']].apply(lambda row: (row['open'] + row['high'] + row['low'] + row['close']) / 4, axis=1)
        self.df['ohlc4'] = (self.df['open'] + self.df['high'] + self.df['low'] + self.df['close']) / 4

        esa = ta.trend.EMAIndicator(close=self.df['ohlc4'], n=WT_CHANNEL_LENGTH, fillna=True)
        self.df['esa'] = esa.ema_indicator()

        de = ta.trend.EMAIndicator(close=(self.df['ohlc4'] - self.df['esa']), n=WT_CHANNEL_LENGTH, fillna=True)
        self.df['de'] = de.ema_indicator()

        self.df['ci'] = (self.df['ohlc4'] - self.df['esa']) / (0.015 * self.df['de'])

        tci = ta.trend.EMAIndicator(close=self.df['ci'], n=WT_AVERAGE_LENGTH, fillna=True)
        self.df['wt1'] = tci.ema_indicator()

        self.df['wt2'] = ta.volatility.keltner_channel_central(high=self.df['wt1'], low=self.df['wt1'], close=self.df['wt1'], n=3, fillna=True) # a hacked sma since ta doesn't have a function for it
        
        self.df['vwap'] = self.df['wt1'] - self.df['wt2']

        self.df['wt_cross'] = self._cross(self.df['wt1'], self.df['wt2'])

        def yellow_x(row):
            return int((row['red_diamond'] == 1) and (row['rsi'] <= 30) and (row['wt2'] <= WT_OVERSOLD_1))

        def blood_diamond(row):
            return int((row['red_diamond'] == 1) and (row['red_x'] == 1))

        ### Signals
        self.df['long_ema'] = self._crossover(self.df['ema_1'], self.df['ema_7'])
        self.df['red_x'] = self._crossunder(self.df['ema_0'], self.df['ema_1'])
        self.df['blue_triangle'] = self._crossover(self.df['ema_1'], self.df['ema_2'])
        self.df['red_diamond'] = self._crossunder(self.df['wt1'], self.df['wt2'])
        self.df['yellow_x'] = self.df.apply(yellow_x, axis=1)
        self.df['blood_diamond'] = self.df.apply(blood_diamond, axis=1)
        self.df['short_ema'] = self._crossover(self.df['ema_7'], self.df['ema_1']) """


        # MarketCipher B Indicators
        # WaveTrend
        self.df['ap'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3.0
        
        esa = ta.trend.EMAIndicator(close=self.df['ap'], n=CHANNEL_LENGTH, fillna=False)
        self.df['esa'] = esa.ema_indicator()

        self.df['d'] = abs(self.df['ap'] - self.df['esa'])
        de = ta.trend.EMAIndicator(close=self.df['d'], n=CHANNEL_LENGTH, fillna=False)
        self.df['de'] = de.ema_indicator()

        self.df['ci'] = (self.df['ap'] - self.df['esa']) / (0.015 * self.df['d'])
        
        tci = ta.trend.EMAIndicator(close=self.df['ci'], n=AVERAGE_LENGTH, fillna=False)
        self.df['tci'] = tci.ema_indicator()

        self.df['wt1'] = self.df['tci'] # LIGHT blue wave
        self.df['wt2'] = self.df.rolling(window=3)['wt1'].mean()

        # RSI's and divergences
        self.df['log_close'] = np.log(self.df['close'])

        rsi1w = ta.momentum.RSIIndicator(close=self.df['log_close'], n=LENGTH_RSI_W, fillna=False)
        self.df['rsi1w'] = rsi1w.rsi()

        kkw = ta.momentum.StochasticOscillator(close=self.df['rsi1w'], high=self.df['rsi1w'], low=self.df['rsi1w'], n=LENGTH_STOCH_W, d_n=SMOOTH_KW, fillna=False)
        self.df['kkw'] = kkw.stoch()

        self.df['dw'] = self.df.rolling(window=SMOOTH_DW)['kkw'].mean()

        
        pd.set_option('display.max_rows', 50)

        self._add_ha_data()

        self.df['ha_candle_val'] = (self.df['ha_close'] - self.df['ha_open']) / (self.df['ha_high'] - self.df['ha_low'])

        self.df['mvc'] = self.df.rolling(window=RSI_MFI_PERIOD)['ha_candle_val'].mean()

        self.df['money_flow'] = self.df['mvc'] * RSI_MFI_MULT

        self.df['wt_cross_up'] = self._crossover(self.df['wt2'], self.df['wt1'])
        self.df['wt_cross_down'] = self._crossover(self.df['wt1'], self.df['wt2'])

    def _add_logic(self):
        """ Define the logic that decides when trades should be entered and exited.
            Adds columns to self.df: 'long', 'short', 'exitlong', 'exitshort'
            You must always add these columns for the backtester to work
        """
        print('adding logic')
        def __long():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt_cross_up'] == 1 and row['wt1'] < -65 and row['money_flow'] >= 0)

            return result
        
        def __short():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt_cross_down'] == 1 and row['wt1'] > 50 and row['money_flow'] < 0)

            return result

        def __exitlong():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['short'] == 1 or row['wt1'] > 78)

            return result

        def __exitshort():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['long'] == 1 or row['wt1'] < -88)

            return result

        self.df['long'] = __long()
        self.df['short'] = __short()
        self.df['exitlong'] = __exitlong()
        self.df['exitshort'] = __exitshort()

        print(self.df)

    def get_actions(self):
        """ Returns which action (if any) to perform, based on the values in the 
            last row of self.df.
        """
        last_row_index = len(self.df) - 1
        ret_list = []

        if self.df.loc[last_row_index]['long'] == 1:
            ret_list.append(Action.OPEN_LONG)
        if self.df.loc[last_row_index]['short'] == 1:
            ret_list.append(Action.OPEN_SHORT)
        if self.df.loc[last_row_index]['exitlong'] == 1:
            ret_list.append(Action.CLOSE_LONG)
        if self.df.loc[last_row_index]['exitshort'] == 1:
            ret_list.append(Action.CLOSE_SHORT)
        
        if (len(ret_list) == 0):
            ret_list.append(Action.NO_ACTION)

        ret_list.sort()

        return ret_list
        
        


if __name__ == '__main__':
    test_strategy = Strategy(data=sample_response.get('result'))


