import json
import time

from bot import TradingBot
from pipelines.wt_pipeline import WTPipeline
from telebot import TelegramBot

from backtest import Backtester
from exchange.bybit_exchange import BybitExchange
from strategies.thm_strategy import THMStrategy

# tele_config = configparser.ConfigParser
# tele_config.read('secret/telegram_keys.ini')

# BOT_TOKEN = str(tele_config['DEFAULT']['BOT_TOKEN'])
# USER_ID = int(tele_config['DEFAULT']['CHAT_ID'])

# if __name__ == '__main__':
#     trading_bot = TradingBot(test=True)
#     telebot = TelegramBot(token=BOT_TOKEN, allowed_user_id=USER_ID, trading_bot=trading_bot)

# config =    {
#                     'bot_token': '1119907117:AAE7yP-2n3JCY0yBJVh1UxubwjIaf4RbsGQ',
#                     'chat_id': 951313615
#                 }

#     with open('secret/telegram_keys.json', 'w') as f:
#         json.dump(config, f)

if __name__ == '__main__':
    ### Running a pipeline

    # Get Data
    exchange = BybitExchange(test=False) # False because we want kline data from the real exchange
    data = exchange.get_klines(symbol="BTCUSD", interval="5", limit=2880)

    thm_strategy = THMStrategy()
    thm_strategy.load_klines(data=data)
    backtester = Backtester(strategy=thm_strategy, pyramiding=15, stake_percent=0.05, initial_capital=1, leverage=5)
    backtester.print_report()
    
    # pipeline = WTPipeline(test=False, data=data)
    # pipeline.run_pipeline()


