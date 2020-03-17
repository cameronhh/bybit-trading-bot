import time

from bot import TradingBot

TIME_PERIOD = 5 # in mins
TIME_PERIOD_SECS = TIME_PERIOD * 60

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
