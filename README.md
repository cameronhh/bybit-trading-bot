# Simple Bybit Trading Bot
Still in development!

A trading bot that can be used with the [Bybit trading platform](https://www.bybit.com/app/exchange/BTCUSD).

Works out of the box with a simple (not profitable) strategy implementation.

You can implement your own stratwegies by inheriting from the BaseStrategy class. See strategies/__init__.py for more information.

# Usage
Clone the repository and set up a python virtual environment.
Install the packages in requirements.txt with pip

You will need to [get an API key and secret](https://help.bybit.com/hc/en-us/articles/360039260974-How-to-add-a-new-API-key-) from Bybit.
Add the values to secret/bybit_keys.json

Running main.py will start the bot using APScheduler. It is effectively a cron job managed by a python program.

Backtesting/Optimising strategies can be done by running testing.py.

See comments for more details.

# Todo
- Run as a service instead of using APScheduler
- Properly implement the pandas/numpy math in strategies to utilise vector operations
- Telegram bot to send messages when the bot takes actions + some sort of intermittent summaries
- Write unit tests for the MockExchange and Backtester
- Add features for Limit orders, stop loss/take profit in TradintBot
- Give the bot an on-tick callback, as opposed to only querying the server when a new candle is ready

# Things I've Learnt
- cron jobs
- How to make a basic Telegram bot
- How to optimise hyperparameters for a model
- Different trading strategies, risk management strategies, technical analysis in general
- Trading manually is more fun
