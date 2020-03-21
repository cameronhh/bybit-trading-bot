import time
from bot import TradingBot
from telebot import TelegramBot


BOT_TOKEN = "1119907117:AAE7yP-2n3JCY0yBJVh1UxubwjIaf4RbsGQ"
USER_ID = 951313615

if __name__ == '__main__':
    trading_bot = TradingBot(test=True)
    telebot = TelegramBot(token=BOT_TOKEN, allowed_user_id=USER_ID, trading_bot=trading_bot)
