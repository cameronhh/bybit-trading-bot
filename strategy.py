import pandas as pd
import numpy as np
import ta



WT_OVERBOUGHT_1 = 53
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
WT_AVERAGE_LENGTH = 12

class Strategy:
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
    """
    def __init__(self, data):
        print('initialising new strategy')
        self.df = pd.DataFrame.from_dict(data)
        
        self.df['interval'] = pd.to_numeric(self.df['interval'])
        self.df['open_time'] = pd.to_numeric(self.df['open_time'])
        self.df['open'] = pd.to_numeric(self.df['open'])
        self.df['high'] = pd.to_numeric(self.df['high'])
        self.df['low'] = pd.to_numeric(self.df['low'])
        self.df['close'] = pd.to_numeric(self.df['close'])
        self.df['volume'] = pd.to_numeric(self.df['volume'])
        self.df['turnover'] = pd.to_numeric(self.df['turnover'])

        self.add_indicators()
        self.add_logic()

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

    def add_indicators(self):
        """ Define the indicators to be used by your strategy in this function.
        """
        print('adding indicators')
        adi = ta.volume.AccDistIndexIndicator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            volume=self.df['volume'],
            fillna=True,
        )
        self.df['adi'] = adi.acc_dist_index()

        # Market Cipher A Indicators

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
        self.df['short_ema'] = self._crossover(self.df['ema_7'], self.df['ema_1'])
        
        print(self.df)



    def add_logic(self):
        """ Define the logic that decides when trades should be entered and exited.
            Adds columns to self.df: 'long', 'short', 'exitlong', 'exitshort'
            You must always add these columns for the backtester to work
        """
        print('adding logic')
        rng = np.random.RandomState(3)
        self.df['long'] = self.df['long_ema']
        self.df['short'] = self.df['short_ema']
        self.df['exitlong'] = self.df['short_ema']
        self.df['exitshort'] = self.df['long_ema']
        


if __name__ == '__main__':
    test_strategy = Strategy(data=sample_response.get('result'))


