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


class THMStrategy():
    """ An example of a (sort of) complex strategy. It's not profitable!
        TODO: Leverage pandas/numpy properly to make adding indicators as efficient as possible.
    """

    def __init__(self, wtsma_length=180, wt_open_long=-55.9, wt_close_long=5, mfi_open_long=-100.0, wt_open_short=40.22, wt_close_short=-10.0, mfi_open_short=100.0):
        self.WTSMA_LENGTH = wtsma_length
        self.WT_OPEN_LONG = wt_open_long
        self.WT_CLOSE_LONG = wt_close_long
        self.MFI_OPEN_LONG = mfi_open_long
        self.WT_OPEN_SHORT = wt_open_short
        self.WT_CLOSE_SHORT = wt_close_short
        self.MFI_OPEN_SHORT = mfi_open_short

    def update_params(self, wtsma_length=180, wt_open_long=-55.9, wt_close_long=5, mfi_open_long=-100.0, wt_open_short=40.22, wt_close_short=-10.0, mfi_open_short=100.0):
        """ Updates the hyperparamteres of this strategy. If function is passed with no parameters then they will reset to default.
            Updating the parameters will also update the long, short, exitlong and exitshort columns of the data. """
        self.WTSMA_LENGTH = wtsma_length
        self.WT_OPEN_LONG = wt_open_long
        self.WT_CLOSE_LONG = wt_close_long
        self.MFI_OPEN_LONG = mfi_open_long
        self.WT_OPEN_SHORT = wt_open_short
        self.WT_CLOSE_SHORT = wt_close_short
        self.MFI_OPEN_SHORT = mfi_open_short

        self._add_signals()

    def load_klines(self, data):
        """ Import a set of klines into this strategy, adding relevant indicators and signals to them """
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
        self._add_signals()

    def _add_indicators(self):
        """ Adds indicators that are involved in this strategy and adds the logic """

        self.df['ap'] = (self.df['high'] + self.df['low'] + self.df['close']) / 3.0
        
        esa = ta.trend.EMAIndicator(close=self.df['ap'], n=CHANNEL_LENGTH, fillna=False)
        self.df['esa'] = esa.ema_indicator()

        self.df['d'] = abs(self.df['ap'] - self.df['esa'])
        de = ta.trend.EMAIndicator(close=self.df['d'], n=CHANNEL_LENGTH, fillna=False)
        self.df['de'] = de.ema_indicator()

        self.df['ci'] = (self.df['ap'] - self.df['esa']) / (0.015 * self.df['de'])
        
        tci = ta.trend.EMAIndicator(close=self.df['ci'], n=AVERAGE_LENGTH, fillna=False)
        self.df['tci'] = tci.ema_indicator()

        self.df['wt1'] = self.df['tci']
        self.df['wt2'] = self.df.rolling(window=3)['wt1'].mean()

        self.df['ha_open'], self.df['ha_close'], self.df['ha_high'], self.df['ha_low'] = indicators.heiken_ashi(self.df)

        self.df['ha_candle_val'] = indicators.candle_value(self.df, ha=False)
        self.df['ha_candle_val_amplified'] = self.df['ha_candle_val'] * 1000

        self.df['mvc'] = self.df.rolling(window=RSI_MFI_PERIOD)['ha_candle_val'].mean()
        self.df['money_flow'] = self.df['mvc'] * RSI_MFI_MULT

        self.df['wt_cross_up'] = indicators.crossover(self.df['wt2'], self.df['wt1'])
        self.df['wt_cross_down'] = indicators.crossover(self.df['wt1'], self.df['wt2'])

        self.df['log_mfi_short'] = indicators.log_mfi(self.df, 'short')
        self.df['log_mfi_long'] = indicators.log_mfi(self.df, 'long')

        self.df['wtsig'] = self.df['wt1'] * abs(self.df['money_flow'])
        self.df['wtsma'] = self.df.rolling(window=self.WTSMA_LENGTH)['wtsig'].mean()


    def _add_signals(self):
        """ Adds four new columns to the data in place.
            'long', 'short', 'exitlong', 'exitshort'
            The four columns are  binary columns. 1 indicates an action and 0 indicates no action.
        """

        def __long():
            """ Returns a pd series of 1s and 0s. """
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] < (self.WT_OPEN_LONG * row['log_mfi_long']) and (row['money_flow'] > self.MFI_OPEN_LONG) and row['wtsma'] > 0)
            return result
        
        def __short():
            """ Returns a pd series of 1s and 0s. """
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int(row['wt1'] > (self.WT_OPEN_SHORT * row['log_mfi_short']) and row['money_flow'] < self.MFI_OPEN_SHORT and row['wtsma'] <= 0)
            return result

        def __exitlong():
            """ Returns a pd series of 1s and 0s. """
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int((row['short'] == 1) or (row['wt1'] > (self.WT_CLOSE_LONG * row['log_mfi_long'])) or (row['wtsma'] <= 0))
            return result

        def __exitshort():
            """ Returns a pd series of 1s and 0s. """
            result = pd.Series(index=self.df.index)
            for index, row in self.df.iterrows():
                result.iloc[index] = int((row['long'] == 1) or (row['wt1'] < (self.WT_CLOSE_SHORT * row['log_mfi_short'])) or (row['wtsma'] > 0))
            return result

        self.df['long'] = __long()
        self.df['short'] = __short()
        self.df['exitlong'] = __exitlong()
        self.df['exitshort'] = __exitshort()
        # only_enter_from_worse()
    
    def only_enter_from_worse(self):
        """ Changes columns 'long' and 'short' such that if in a long position,
            the strategy will only recommend a long action when 'long' is true
            AND the close price of that candle is LOWER. Opposite is true
            when a short position is open.

            TODO: this should be logical part of the strategy itself and not an afterthought
                - that is, a strategy should utilise some information about if a position is 
                open or not and whether or not to increase the position size in the relevant
                __long, __exitlong, ...,  etc,  functions.
        """
        cur_pos, pos_entry, pos_size = None, None, 0
        for index, row in self.df.iterrows():
            if cur_pos == None:
                if row['long'] == 1:
                    cur_pos = 'long'
                    pos_entry = row['close']
                    pos_size = 1
                elif row['short'] == 1:
                    cur_pos = 'short'
                    pos_entry = row['close']
                    pos_size = 1
            elif cur_pos == 'long':
                if row['exitlong'] == 1:
                    cur_pos = None
                    pos_entry = None
                    pos_size = 0
                elif row['long'] == 1:
                    if row['close'] > pos_entry:
                        self.df.at[index, 'long'] = 0
                    else:
                        pos_size += 1
                        pos_entry = (pos_entry * (pos_size - 1) + row['close']) / pos_size
            elif cur_pos == 'short':
                if row['exitshort'] == 1:
                    cur_pos = None
                    pos_entry = None
                    pos_size = 0
                elif row['short'] == 1:
                    if row['close'] < pos_entry:
                        self.df.at[index, 'short'] = 0
                    else:
                        pos_size += 1
                        pos_entry = (pos_entry * (pos_size - 1) + row['close']) / pos_size

    def get_num_candles(self):
        return len(self.df)
    
    def print_df(self):
        with pd.option_context('display.max_rows', 10):  # more options can be specified also
            print(self.df)

    def get_actions(self, index=None):
        """ Returns which actions.Action to perform, based on the values 
            in the second last row of self.df.
            Second last row is used as the last row returned by Bybit
            exchange data is the present, incomplete candle.
        """

        if index == None:
            index = len(self.df) - 2
        ret_list = []

        if self.df.loc[index]['exitlong'] == 1:
            ret_list.append(Action.CLOSE_LONG)
        if self.df.loc[index]['exitshort'] == 1:
            ret_list.append(Action.CLOSE_SHORT)
        if self.df.loc[index]['long'] == 1:
            ret_list.append(Action.OPEN_LONG)
        if self.df.loc[index]['short'] == 1:
            ret_list.append(Action.OPEN_SHORT)
        
        if (len(ret_list) == 0):
            ret_list.append(Action.NO_ACTION)

        return ret_list
