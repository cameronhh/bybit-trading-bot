
"""
General Notes:
    - project will be a 'forgetful' bot, meaning that it only stores enough data for it to calculate the indicators it uses
    - forgetful also means that it will not need a database
    - future intention is that it is not forgetful and stores everything
    - there is an indicator library called 'ta' which can be used for most of the technical analysis

Project structure:
    - Bybit Client (downloaded)
    - Kline data
        - download from coinbase api - as data is better than the bybit API
        - do technical analysis on the data
        - define different states based on the technical analysis
    - Logic for the client
        - different actions based on different states
        - stake size / risk management
        - etc.

"""

TIME_PERIOD = 15 # in mins
TIME_PERIOD_SECS = TIME_PERIOD * 60

from bot import TradingBot
import time


def main():

    cur_time = int(time.time()) % TIME_PERIOD_SECS
    time_remaining = TIME_PERIOD_SECS - cur_time

    if time_remaining > 60:
        print(f"{time_remaining} seconds until next candle, exiting until next job...")
        return
    
    print(f"{time_remaining} seconds until next candle, continuing...")

    bot = TradingBot()
    while cur_time > 5:
        time_to_sleep = max(0, time_remaining - 10)

        print(f"Sleeping for {time_to_sleep} seconds...")

        time.sleep(time_to_sleep)

        cur_time = int(time.time()) % TIME_PERIOD_SECS
        time_remaining = TIME_PERIOD_SECS - cur_time

    bot.worker()


if __name__ == '__main__':
    main()
