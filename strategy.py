import numpy as np
import pandas as pd
import ta

from actions import Action

class BaseStrategy():
    """ A Strategy manages generation of indicators on kline data and
        interpretting when actions should take place.
        Must call Strategy.load_klines before using Strategy.get_action

        Usage guide: 
            Inherit from this class, define any parameters in the constructor.
            Overwrite add_indicators to add custom signals/indicators to 
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

    def _add_indicators(self):
        """ This method should only add new columns to self.df.
        """
        pass

    def _add_logic(self):
        """ This method should add columns 'long', 'short', 'exitlong' and 'exitshort'
            to self.df.
        """
        pass

if __name__ == '__main__':
    test_strategy = Strategy(data=sample_response.get('result'))
