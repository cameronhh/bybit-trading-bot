from datetime import datetime
import json
import logging
import time

import bybit

class BybitExchange:
    def __init__(self, test=True):

        logging.basicConfig(filename="logs/bybit_exchange.log", format='%(asctime)s %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.info("----------------")
        self.logger.info("Starting Bybit exchange client")

        self.test = test
        api_key, api_secret = self._get_keys()
        self.client = bybit.bybit(test=test, api_key=api_key, api_secret=api_secret)
    
    def _get_keys(self):
        with open('secret/bybit_keys.json', 'r') as f:
            key_config = json.load(f)

        key_dict = key_config['testnet'] if self.test else key_config['mainnet']        
        return key_dict['api_key'], key_dict['api_secret']

    def get_available_balance(self, coin):
        kwargs = { "coin": coin }
        response = self.client.Wallet.Wallet_getBalance(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_available_balance: returned {response.get('result').get(coin).get('available_balance')}")
            return response.get('result').get(coin).get('available_balance')
        else:
            self.logger.error("[BYBIT CLIENT] get_availlable_balance: bad request")

    def get_equity(self, coin):
        kwargs = { "coin": coin }
        response = self.client.Wallet.Wallet_getBalance(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_equity: returned {response.get('result').get(coin).get('available_balance')}")
            return response.get('result').get(coin).get('equity')
        else:
            self.logger.error("[BYBIT CLIENT] get_equity: bad request")

    def get_time(self):
        response = self.client.Common.Common_get().result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_time: returned {response.get('time_now')}")
            return response.get('time_now')
        else:
            self.logger.error("[BYBIT CLIENT] get_time: bad request")

    def get_market_price(self, symbol):
        kwargs = { "symbol": symbol }
        response = self.client.Market.Market_symbolInfo(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_market_price: returned {response.get('result')[0].get('mark_price')}")
            return float(response.get('result')[0].get('mark_price'))
        else:
            self.logger.error("[BYBIT CLIENT] get_market_price: bad request")

    def place_order(self, side, symbol, contracts):
        kwargs = {  "side": side,
                    "symbol": symbol,
                    "order_type": "Market",
                    "qty": contracts,
                    # "price": ,
                    "time_in_force": "GoodTillCancel",
                    # "take_profit": ,
                    # "stop_loss": ,
                    # "reduce_only": ,
                    # "close_on_trigger": ,
                    # "order_link_id": 
                }
        response = self.client.Order.Order_newV2(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] place_order: returned {response.get('result')}")
            return 0
        else:
            self.logger.error("[BYBIT CLIENT] place_order: bad request")
            return -1

    def get_position(self, symbol):
        kwargs = {"symbol" : symbol}
        response = self.client.Positions.Positions_myPositionV2(**kwargs).result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_position: returned {response.get('result')}")
            return response.get('result')
        else:
            self.logger.error("[BYBIT CLIENT] get_position: bad request")

    def get_leverage(self, symbol):
        response = self.client.Positions.Positions_userLeverage().result()[0]
        if response.get('ret_msg') == 'OK':
            self.logger.info(f"[BYBIT CLIENT] get_leverage: returned {response.get('result').get(symbol).get('leverage')}")
            return response.get('result').get(symbol).get('leverage')
        else:
            self.logger.error("[BYBIT CLIENT] get_leverage: bad request")

    def set_leverage(self, symbol, leverage):
        if (self.get_leverage(symbol) != int(leverage)):
            kwargs = { "symbol": symbol, "leverage": leverage }
            response = self.client.Positions.Positions_saveLeverage(**kwargs).result()[0]
            if response.get('ret_msg') == 'OK':
                self.logger.info(f"[BYBIT CLIENT] set_leverage: returned {response.get('result')}")
                return response.get('result')
            else:
                self.logger.error("[BYBIT CLIENT] set_leverage: bad request")
        self.logger.info(f'[BYBIT CLIENT] set_leverage: Leverage already {leverage}')

    def _int_from_interval(self, interval):
        if interval in ["1", "3", "5", "15", "30", "60", "120", "240", "360", "720"]:
            return int(interval)
        elif interval == "D":
            return 24 * 60
        elif interval == "W":
            return 24 * 60 * 7
        # monthly and yearly not supported

    def _get_klines_from_range(self, symbol, interval, start_time, end_time):
        _interval_secs = self._int_from_interval(interval) * 60

        cur_time = start_time
        result = []
        while cur_time < end_time:
            kwargs = {"symbol": symbol, "interval": interval, "from": cur_time}
            result += self.client.Kline.Kline_get(**kwargs).result()[0].get('result')
            cur_time += 200 * _interval_secs
            time.sleep(0.1)
        return result

    def _get_klines_from_limit(self, symbol, interval, limit):
        _interval_secs = self._int_from_interval(interval) * 60
        start_time = int(time.time()) - (limit * _interval_secs)
        return self._get_klines_from_range(symbol, interval, start_time, int(time.time()))

    def get_klines(self, symbol="BTCUSD", interval="1", start_time=None, end_time=None, limit=200, ):
        """ start_time and end_time should be of the format `YYYY-MM-DD HH:MM`
        """
        interval = str(interval)

        self.logger.info(f"[BYBIT CLIENT] get_klines: {limit} candles requested for interval {interval} from {start_time} to {end_time}")

        if start_time != None:
            start_time = int(datetime.fromisoformat(start_time).timestamp())
            if end_time == None:
                end_time = int(time.time())
            else:
                end_time = int(date.fromisoformat(end_time).timestamp())
            return self._get_klines_from_range(symbol, interval, start_time, end_time)
        return self._get_klines_from_limit(symbol, interval, limit)

    def analyse_history(self):
        # look at trading history and generate some metrics
        raise NotImplementedError
