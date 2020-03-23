import numpy as np
import pandas as pd
import ta

from enums.actions import Action
import indicators
from strategies import BaseStrategy

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

BEAR_MARKET = 0
BULL_MARKET = 1
UNCERTAINTY = 2

class THMStrategy(BaseStrategy):
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
        Must call Strategy.load_klines before using Strategy.get_action

        This particular strategy is a wave trend strategy that trades
        on the 5 minute chart. It has 3 states, all with different execution 
        logic. The state its in is dependent on the current value of the 
        moneyflow of the 2 hour chart.

        STATE = 0: Means 2H MFI <= -5
        STATE = 1: Means 2H MFI >= 5
        STATE = 2: Means -5 < 2H MFI < 5
    """

    def __init__(self):
        super().__init__()

        self.state = BEAR_MARKET
        self.WT_OPEN_LONG = -28.9
        self.WT_CLOSE_LONG = 79.21
        self.MFI_OPEN_LONG = 31.0
        self.WT_OPEN_SHORT = 40.22
        self.WT_CLOSE_SHORT = 1.0
        self.MFI_OPEN_SHORT = 24

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

        self.df['log_mfi'] = indicators.log_mfi(self.df)

    def _add_logic(self):
        super()._add_logic()

        def __long():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] < (self.WT_OPEN_LONG * row['log_mfi']) and row['money_flow'] > self.MFI_OPEN_LONG and self.state == BULL_MARKET)
            return result
        
        def __short():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] > (self.WT_OPEN_SHORT * row['log_mfi']) and row['money_flow'] < self.MFI_OPEN_SHORT and self.state == BEAR_MARKET)
            return result

        def __exitlong():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['short'] == 1 or row['wt1'] > self.WT_CLOSE_LONG)
            return result

        def __exitshort():
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['long'] == 1 or row['wt1'] < self.WT_CLOSE_SHORT)
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

        if self.df.loc[last_row_index]['exitlong'] == 1:
            ret_list.append(Action.CLOSE_LONG)
        if self.df.loc[last_row_index]['exitshort'] == 1:
            ret_list.append(Action.CLOSE_SHORT)
        if self.df.loc[last_row_index]['long'] == 1:
            ret_list.append(Action.OPEN_LONG)
        if self.df.loc[last_row_index]['short'] == 1:
            ret_list.append(Action.OPEN_SHORT)
        
        if (len(ret_list) == 0):
            ret_list.append(Action.NO_ACTION)

        return ret_list




"""

The strategy:

logMoneyFlow = log10(10 + abs(moneyFlow)) //////// important

longCondition = (wt1 < (-26.9 * logMoneyFlow) and moneyFlow > 31)
shortCondition = (wt1 > (39.22 * logMoneyFlow) and moneyFlow < 14.65)

exitLong = shortCondition or (wt1 > 79.21)
exitShort = longCondition or (wt1 < 15.98) 



"""