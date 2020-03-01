import pandas as pd
import ta

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

    def add_indicators(self):
        """ Define the indicators to be used by your strategy in this function.
        """
        print('adding indicators')
        indicator_adi = ta.volume.AccDistIndexIndicator(
            high=self.df['high'],
            low=self.df['low'],
            close=self.df['close'],
            volume=self.df['volume'],
            fillna=False,
        )
        self.df['adi'] = indicator_adi.acc_dist_index()

        # add more indicators here
        print(self.df)

    def add_logic(self):
        """ Define the logic that decides when trades should be entered and exited.
            Adds columns to self.df: 'long', 'short', 'exitlong', 'exitshort'
        """
        print('adding logic')

