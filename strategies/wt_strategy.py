from strategy import BaseStrategy
import pandas as pd
import numpy as np
import ta
from actions import Action
import indicators


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

class WTStrategy(BaseStrategy):
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
        Must call Strategy.load_klines before using Strategy.get_action
    """
    def __init__(self, wt_open_long=-65, wt_open_short=50, mfi_open=0, mfi_close=0, wt_exit_long=78, wt_exit_short=-88):
        super().__init__()

        self.WT_OPEN_LONG_THRESHOLD = wt_open_long
        self.WT_OPEN_SHORT_THRESHOLD = wt_open_short
        self.MFI_OPEN_THRESHOLD = mfi_open
        self.MFI_CLOSE_THRESHOLD = mfi_open
        self.WT_EXIT_LONG_THRESHOLD = wt_exit_long
        self.WT_EXIT_SHORT_THRESHOLD = wt_exit_short
        
    def load_klines(self, data):
        super().load_klines(data)
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
        super()._add_indicators()

        # WaveTrend
        self.df['ap'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3.0
        
        esa = ta.trend.EMAIndicator(close=self.df['ap'], n=CHANNEL_LENGTH, fillna=True)
        self.df['esa'] = esa.ema_indicator()

        self.df['d'] = abs(self.df['ap'] - self.df['esa'])
        de = ta.trend.EMAIndicator(close=self.df['d'], n=CHANNEL_LENGTH, fillna=True)
        self.df['de'] = de.ema_indicator()

        self.df['ci'] = (self.df['ap'] - self.df['esa']) / (0.015 * self.df['de'])
        
        tci = ta.trend.EMAIndicator(close=self.df['ci'], n=AVERAGE_LENGTH, fillna=True)
        self.df['tci'] = tci.ema_indicator()

        self.df['wt1'] = self.df['tci'] # LIGHT blue wave
        self.df['wt2'] = self.df.rolling(window=3)['wt1'].mean()

        self.df['ha_open'], self.df['ha_close'], self.df['ha_high'], self.df['ha_low'] = indicators.heiken_ashi(self.df)

        self.df['ha_candle_val'] = (self.df['ha_close'] - self.df['ha_open']) / (self.df['ha_high'] - self.df['ha_low'])
        # self.df['ha_candle_val'] = (self.df['close'] - self.df['open']) / (self.df['high'] - self.df['low'])

        self.df['mvc'] = self.df.rolling(window=RSI_MFI_PERIOD)['ha_candle_val'].mean()

        self.df['money_flow'] = self.df['mvc'] * RSI_MFI_MULT

        self.df['wt_cross_up'] = indicators.crossover(self.df['wt2'], self.df['wt1'])
        self.df['wt_cross_down'] = indicators.crossover(self.df['wt1'], self.df['wt2'])

        self.df['log_mfi'] = np.log10(10 + abs(self.df['money_flow']))

    def _add_logic(self):
        super()._add_logic()

        # print('adding logic')
        def __long():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] < self.WT_OPEN_LONG_THRESHOLD and row['money_flow'] > self.MFI_OPEN_THRESHOLD) # and row['wt_cross_up'] == 1)

            return result
        
        def __short():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] > self.WT_OPEN_SHORT_THRESHOLD and row['money_flow'] < self.MFI_CLOSE_THRESHOLD) # and row['wt_cross_down'] == 1)

            return result

        def __exitlong():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['short'] == 1 or row['wt1'] > self.WT_EXIT_LONG_THRESHOLD)

            return result

        def __exitshort():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['long'] == 1 or row['wt1'] < self.WT_EXIT_SHORT_THRESHOLD)

            return result

        self.df['long'] = __long()
        self.df['short'] = __short()
        self.df['exitlong'] = __exitlong()
        self.df['exitshort'] = __exitshort()

        # print(self.df)

    def get_actions(self):
        """ Returns which action (if any) to perform, based on the values in the 
            last row of self.df.
        """
        last_row_index = len(self.df) - 2 # -2 because the last row will always be the currently incomplete candle
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