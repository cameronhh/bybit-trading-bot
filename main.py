import logging
import time

from apscheduler.schedulers.blocking import BlockingScheduler

from bot import TradingBot
from pipeline.wt_pipeline import WTPipeline

logging.basicConfig( level=logging.DEBUG, # TODO: work out how to do logging properly
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    filename='logs/sandbox.log',
                    filemode='w')

sched = BlockingScheduler({ # TODO separate this out into a config file
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': '20'
    },
    'apscheduler.executors.processpool': {
        'type': 'processpool',
        'max_workers': '5'
    },
    'apscheduler.job_defaults.coalesce': 'false',
    'apscheduler.job_defaults.max_instances': '3',
    'apscheduler.timezone': 'UTC',
})

logger = logging.getLogger("sandbox")

TIME_PERIOD_SECS = 300
@sched.scheduled_job('cron', year='*', month='*', day='*', week='*', day_of_week='*', hour='*', minute='4,9,14,19,24,29,34,39,44,49,54,59', second='50')
def trade_job():
    logger.debug(f"running trade job at time: {time.gmtime()}")
    bot = TradingBot(test=True)
    while int(time.time()) % TIME_PERIOD_SECS != 0:
        pass
    bot.worker()

# @sched.scheduled_job('cron', year='*', month='*', day='*', week='*', day_of_week='*', hour='0,2,4,6,8,10,12,14,16,18,20,22,', minute='0', second='0')
# def backtest_job():
#     logger.debug(f"running backtest job at time: {time.gmtime()}")
#     pipeline = WTPipeline(test=True, load_klines=True, validate=False)
#     pipeline.run_pipeline()

sched.start()