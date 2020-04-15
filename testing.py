import json
import time

from bot import TradingBot
from pipelines.thm_pipeline import THMPipeline

from backtest import Backtester
from exchange.bybit_exchange import BybitExchange
from strategies.thm_strategy import THMStrategy

def test_pipeline(load_file='', optimise=False, train_test_split=0.5, num_candles=1000, interval="5"):
    optimise = False
    n_candles = num_candles

    strat = THMStrategy()

    if load_file != '':
        with open(load_file, 'r') as f:
            data = json.load(f)
    else:
        exch = BybitExchange(test=False)
        data = exch.get_klines(symbol="BTCUSD", interval=interval, limit=n_candles)

    print(f"Loaded data.")

    strat.load_klines(data)

    print(f"Added indicators and signals.")

    bt = Backtester(strategy=strat, pyramiding=15, stake_percent=0.05, leverage=5.0)

    if optimise:
        optimiser = THMPipeline(backtester=bt, num_candles=n_candles, train_test_split=train_test_split)
        optimiser.run_pipeline()
    else:
        bt.run_backtest(start_index=0)
        bt.print_report()

if __name__ == '__main__':
    test_pipeline(num_candles=2880)
