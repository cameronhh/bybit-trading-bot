
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

from bot import TradingBot
import time


def main():
    bot = TradingBot()

    cur_time = int(time.time()) % 300
    
    while cur_time != 0:
        time_to_sleep = max(300 - cur_time - 5, 0)

        print(f"Sleeping for {time_to_sleep} seconds...")

        time.sleep(time_to_sleep)
        
        cur_time = int(time.time()) % 300

    bot.worker()


if __name__ == '__main__':
    main()
