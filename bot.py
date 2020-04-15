import configparser
import logging
import time

from enums.actions import Action
from exchange.bybit_exchange import BybitExchange
from strategies.thm_strategy import THMStrategy

class TradingBot:
    def __init__(self, test=True):
        logging.basicConfig(filename="logs/bot.log", format='%(asctime)s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("----------------")
        self.logger.info("Starting Trading Bot")

        self.strategy = THMStrategy() # see BaseStrategy to see what defines a strategy

        # can customise these variables
        self.risk = 0.05
        self.leverage = 5

        self.exchange = BybitExchange(test=True)
        self.exchange.set_leverage("BTCUSD",  str(self.leverage))
        self.update_info()

    def update_info(self):
        self.logger.info("[BOT] updating info")
        # check position
        self.position = self.exchange.get_position("BTCUSD")
        self.has_position = not (self.position.get('side') == 'None')
        self.avail_bal = self.exchange.get_available_balance("BTC")
        self.equity = self.exchange.get_equity("BTC")
        # get last seen price
        self.last_mark_price = self.exchange.get_market_price("BTCUSD")

    def new_order_qty(self, coin):
        # return self.avail_bal * self.risk * self.leverage * self.last_mark_price # uncomment for dynamic position sizing
        return self.equity * self.risk * self.leverage * self.last_mark_price

    def execute_action(self, action):
        if action == Action.NO_ACTION:
            self.logger.info("[BOT] executing NO_ACTION")
        elif action == Action.CLOSE_LONG:
            self.logger.info(f"[BOT] executing CLOSE_LONG")
            if self.position.get('side') == 'Buy': # in a long posn
                open_qty = self.position.get('size')
                self.exchange.place_order('Sell', 'BTCUSD', open_qty)
            # else: # not in a long posn
        elif action == Action.CLOSE_SHORT:
            self.logger.info(f"[BOT] executing CLOSE_SHORT")
            if self.position.get('side') == 'Sell': # in a short posn
                open_qty = self.position.get('size')
                self.exchange.place_order('Buy', 'BTCUSD', open_qty)
            # else: # not in a short posn
        elif action == Action.OPEN_LONG:
            self.logger.info(f"[BOT] executing OPEN_LONG")
            qty = self.new_order_qty("BTC")
            self.exchange.place_order("Buy", "BTCUSD", qty)
        elif action == Action.OPEN_SHORT:
            self.logger.info(f"[BOT] executing OPEN_SHORT")
            qty = self.new_order_qty("BTC")
            self.exchange.place_order("Sell", "BTCUSD", qty)
        # update info as action is completed
        self.update_info()


    def worker(self):
        """ Run each time new kline data is ready.
        """
        self.logger.info('[BOT] running worker')

        # get data
        kline_data = self.exchange.get_klines(symbol="BTCUSD", interval="5", limit=200)

        # load data
        self.strategy.load_klines(data=kline_data)

        # get action
        actions = self.strategy.get_actions()
        print(actions)

        for x in actions:
            self.execute_action(x)
