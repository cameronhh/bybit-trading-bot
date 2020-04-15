import numpy as np
import pandas as pd
import ta

from enums.actions import Action

class BaseStrategy():
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
        Must call Strategy.load_klines before using Strategy.get_action

        Usage: 
            Inherit from this class. In order for a strategy to work 
            with the TradingBot class self.df must have atleasts 4 columns:
                'long', 'exitlong', 'short', 'exitshort',
            of 1s and 0s.
    """
    def __init__(self):
        pass        

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
        self._add_signals()

    def _add_indicators(self):
        """ This method should only add new columns to self.df.
        """
        pass

    def _add_signals(self):
        """ This method should add columns 'long', 'short', 'exitlong' and 'exitshort'
            to self.df.
        """
        pass

if __name__ == '__main__':
    test_strategy = Strategy(data=sample_response.get('result'))
