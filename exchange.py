
import bybit, time
from datetime import datetime

class BybitExchange:
    def __init__(self, test=True, api_key="", private_key=""):
        self.client = bybit.bybit(test=True, api_key=api_key, api_secret=private_key)
    
    def get_available_balance(self, coin):
        kwargs = { "coin": coin }
        return self.client.Wallet.Wallet_getBalance(**kwargs).result()[0].get('result').get(coin).get('available_balance')
        
    def get_time(self):
        return self.client.Common.Common_get().result()[0].get('time_now')

    def get_market_price(self, symbol):
        kwargs = { "symbol": symbol }
        return self.client.Market.Market_symbolInfo(**kwargs).result()[0].get('result')[0].get('mark_price')

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
        print(self.client.Order.Order_newV2(**kwargs).result())

    def get_position(self, symbol):
        kwargs = {"symbol" : symbol}
        return self.client.Positions.Positions_myPositionV2(**kwargs).result()[0].get('result')

    def get_leverage(self, symbol):
        return self.client.Positions.Positions_userLeverage().result()[0].get('result').get(symbol).get('leverage')

    def set_leverage(self, symbol, leverage):
        if (self.get_leverage(symbol) != int(leverage)):
            kwargs = { "symbol": symbol, "leverage": leverage }
            return self.client.Positions.Positions_saveLeverage(**kwargs).result()
        return f'Leverage already {leverage}'

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
            time.sleep(0.5)
        return result

    def _get_klines_from_limit(self, symbol, interval, limit):
        _interval_secs = self._int_from_interval(interval) * 60
        start_time = int(time.time()) - (limit * _interval_secs)
        return self._get_klines_from_range(symbol, interval, start_time, int(time.time()))

    def get_klines(self, symbol="BTCUSD", interval="1", start_time=None, end_time=None, limit=200, ):
        """ start_time and end_time should be of the format `YYYY-MM-DD HH:MM`
        """
        interval = str(interval)

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
        priont('not yet implemented')
