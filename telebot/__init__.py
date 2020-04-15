import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import JobQueue
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler
from telegram.ext import BaseFilter
from telegram.ext import run_async
from telegram.ext import Filters

from bot import TradingBot

""" Playing around with a telegram bot to send updates to my phone when actions are executed
    TODO: more on this

"""

with open('secret/telegram_keys.json', 'r') as f:
    user_info = json.load(f)

print(user_info)

class TelegramBot:
    def __init__(self, token: str, allowed_user_id, trading_bot: TradingBot):
        # self.updater = Updater(token=token, use_context=True)
        self.updater = Updater(token=token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.job_queue = self.updater.job_queue
        self.trading_bot = trading_bot
        self.exchange = self.trading_bot.exchange
        
        self._prepare()

        self.updater.start_polling()
        self.updater.idle()

    def _prepare(self):
        def hello(update, context):
            print(update.message.chat_id)
            if int(update.message.chat_id) != CHAT_ID:
                return
            update.message.reply_text(f"cute! hello {update.message.from_user.first_name}! i am autobot rollout")

        self.dispatcher.add_handler(CommandHandler('hello', hello))
