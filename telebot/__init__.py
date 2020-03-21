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

TRADE_SELECT = "trade_select"
SHORT_TRADE = "short_trade"
LONG_TRADE = "long_trade"
OPEN_ORDERS = "open_orders"
FREE_BALANCE = "free_balance"

CANCEL_ORD = "cancel_order"
PROCESS_ORD_CANCEL = "process_ord_cancel"

COIN_NAME = "coin_name"
PERCENT_CHANGE = "percent_select"
AMOUNT = "amount"
PRICE = "price"
PROCESS_TRADE = "process_trade"

CONFIRM = "confirm"
CANCEL = "cancel"
END_CONVERSATION = ConversationHandler.END


CHAT_ID = 951313615


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

            




# updater = Updater(token="1119907117:AAE7yP-2n3JCY0yBJVh1UxubwjIaf4RbsGQ", use_context=True)
# dispatcher = updater.dispatcher

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)

# def alarm(context):
#     """Send the alarm message."""
#     job = context.job
#     context.bot.send_message(job.context, text='Beep!')

# start_handler = CommandHandler('start', start)
# dispatcher.add_handler(start_handler)

# updater.start_polling()