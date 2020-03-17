import configparser
import time

from actions import Action
from exchange import BybitExchange
from strategies.wt_strategy import WTStrategy

class TradingBot:
    def __init__(self, test=True):
        key_config = configparser.ConfigParser()
        key_config.read('keys.ini')

        self.api_key = key_config['TESTNET']['API_KEY'] if test else key_config['MAINNET']['API_KEY']
        self.private_key = key_config['TESTNET']['API_SECRET'] if test else key_config['MAINNET']['API_SECRET']

        self.risk = 0.05     # 5% of available balance staked per trade
        self.leverage = 5

        # init
        self.exchange = BybitExchange(test=True, api_key=self.api_key, private_key=self.private_key)

        strategy_config = configparser.ConfigParser()
        strategy_config.read('config.ini')
        self.strategy = WTStrategy(
            wt_open_long = float(strategy_config['DEFAULT']['WT_OPEN_LONG_THRESHOLD']),
            wt_open_short = float(strategy_config['DEFAULT']['WT_OPEN_SHORT_THRESHOLD']),
            mfi_open = float(strategy_config['DEFAULT']['MFI_OPEN_THRESHOLD']),
            mfi_close = float(strategy_config['DEFAULT']['MFI_CLOSE_THRESHOLD']),
            wt_exit_long = float(strategy_config['DEFAULT']['WT_EXIT_LONG_THRESHOLD']),
            wt_exit_short = float(strategy_config['DEFAULT']['WT_EXIT_SHORT_THRESHOLD']),
        )

        # check leverage
        self.exchange.set_leverage("BTCUSD",  "5")

        self.update_info()


    def testing(self):
        print(f'current available balance is: {self.exchange.get_available_balance("BTC")}')
        print(f'current mark price is: {self.exchange.get_market_price("BTCUSD")}')

    def update_info(self):
        # check position
        self.position = self.exchange.get_position("BTCUSD")
        self.has_position = not (self.position.get('side') == 'None')
        self.avail_bal = self.exchange.get_available_balance("BTC")
        
        # get last seen price
        self.last_mark_price = self.exchange.get_market_price("BTCUSD")

    def new_order_qty(self, coin):
        return self.avail_bal * self.risk * self.leverage * self.last_mark_price

    def execute_action(self, action):
        if action == Action.NO_ACTION:
            print(f"{time.time()} doing NO_ACTION")
            return
    
        elif action == Action.CLOSE_LONG:
            print(f"{time.time()} doing CLOSE_LONG")
            if self.position.get('side') == 'Buy': # in a long posn
                open_qty = self.position.get('size')
                self.exchange.place_order('Sell', 'BTCUSD', size)
            # else: # not in a long posn

        elif action == Action.CLOSE_SHORT:
            print(f"{time.time()} doing CLOSE_SHORT")
            if self.position.get('side') == 'Sell': # in a short posn
                open_qty = self.position.get('size')
                self.exchange.place_order('Buy', 'BTCUSD', size)
            # else: # not in a short posn

        elif action == Action.OPEN_LONG:
            print(f"{time.time()} doing OPEN_LONG")
            qty = self.new_order_qty("BTC")
            self.exchange.place_order("Buy", "BTCUSD", qty)

        elif action == Action.OPEN_SHORT:
            print(f"{time.time()} doing OPEN_SHORT")
            qty = self.new_order_qty("BTC")
            self.exchange.place_order("Sell", "BTCUSD", qty)

        # update info as action is completed
        self.update_info()


    def worker(self):
        """ Run each time new kline data is ready.
        """
        # get data
        kline_data = self.exchange.get_klines(symbol="BTCUSD", interval="15", limit=200)
        # load data
        self.strategy.load_klines(data=kline_data)
        # get action
        actions = self.strategy.get_actions()


        for x in actions:
            self.execute_action(x)

        # if self.exchange.get_leverage("BTCUSD") == 5:
        #     self.exchange.set_leverage("BTCUSD", "10")
        # else:
        #     self.exchange.set_leverage("BTCUSD", "5")


