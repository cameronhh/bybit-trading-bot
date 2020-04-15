import copy
import logging
import time

import numpy as np

NO_POSITION = 0
LONG_OPEN = 1
SHORT_OPEN = 2

class MockExchange:
    def __init__(self, initial_capital=1, leverage=5, commission=0.00075):
        logging.basicConfig(filename="logs/mock_exchange.log", format='%(asctime)s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("----------------")
        self.logger.info("Starting Mock exchange client")

        self.capital = initial_capital
        self.leverage = leverage
        self.commission = commission
        self.position = None
        self.trading_history = []        

    def open_position(self, long=True, margin=0.2, contracts=100, cur_price=0, fee=0):
        side = "Buy" if long else "Sell"
        self.logger.info(f"[MOCK EXCHANGE] open_position: side: {side} - size: {contracts} - price: {cur_price}")
        self.position = Position(long, margin, contracts, cur_price, self.leverage, fee=fee)

    def increase_posn(self, margin, contracts, entry_price, fee=0):
        self.logger.info(f"[MOCK EXCHANGE] increase_posn: increased size: {contracts} - price: {entry_price}")
        self.position.increase_posn(margin=margin, contracts=contracts, entry_price=entry_price, fee=fee)

    def close_position(self, cur_price):
        self.logger.info(f"[MOCK EXCHANGE] close_position: close price: {cur_price}")
        self.init_margin, self.realised_pl, self.fee = self.position.close(cur_price)
        self.trading_history.append(self.position)
        self.position = None
        return self.init_margin, self.realised_pl, self.fee

    def analyse_history(self):
        # look at trading history and generate some metrics            
        return self.trading_history, self.position

class Position:
    def __init__(self, long=True, margin=0.2, contracts=100, start_price=0.0, leverage=5, fee=0):
        self.long = long
        self.contracts = contracts
        self.average_entry_price = start_price
        self.leverage = leverage
        self.margin = margin
        self.contract_value_in_currency = (self.contracts / start_price)
        self.opening_fees = fee

    def increase_posn(self, margin=0.2, contracts=100, entry_price=0.0, fee=0):
        self.contracts += contracts
        self.margin += margin
        self.contract_value_in_currency += (contracts / entry_price)
        self.average_entry_price = self.contracts / self.contract_value_in_currency
        self.opening_fees += fee

    def close(self, end_price=1):
        """ Return the realised P&L of this position, minus fees
        """
        self.end_price = end_price
        self.closing_fee = (self.contracts / end_price) * (0.00075)

        if self.long:
            self.realised_pl = self.contracts * (1 / self.average_entry_price - 1 / self.end_price)
            return self.margin, self.realised_pl, self.closing_fee
        else: # !self.long
            self.realised_pl = self.contracts * (1 / self.end_price - 1 / self.average_entry_price)
            return self.margin, self.realised_pl, self.closing_fee

    def get_unrealised_pl(self, cur_price):
        if self.long:
            return self.contracts * (1 / self.average_entry_price - 1 / cur_price)
        else: #!self.long
            return self.contracts * (1 / cur_price - 1 / self.average_entry_price)

    # TODO: Work out if an order has been liquidated/hit its stop loss/hit its take profit

    def __str__(self):
        side = 'Long' if self.long else 'Short'
        return f"{side}\tmargin={self.margin:.2f}\topen={self.average_entry_price:.2f}\tclose={self.end_price:.2f}\trealised_pl={self.realised_pl:.4f}\tfee={self.closing_fee}"
