
import bybit, time

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
        

    def get_klines(self, symbol, interval):
        """ Get kline data
            - TODO: Make this more robust,
            - turn into a class that can get a ticker as well?
        """
        kwargs = {"symbol": symbol, "interval": interval, "from": (int(time.time()) - 200*300)}
        return self.client.Kline.Kline_get(**kwargs).result()

    def analyse_history(self):
        # look at trading history and generate some metrics
        priont('not yet implemented')
