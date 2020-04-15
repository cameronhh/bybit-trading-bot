from datetime import datetime
import time

import optuna
import pandas as pd
import ta

from backtest import Backtester
from exchange.bybit_exchange import BybitExchange
from strategies.wt_strategy import WTStrategy
from strategies.thm_strategy import THMStrategy

class THMPipeline:
    def __init__(self, backtester=None, num_candles=None, train_test_split=1.0):
        self.bt = backtester
        self.split_index = int(num_candles * train_test_split)

    def run_pipeline(self):
        cur_wt_open_long = self.bt.strategy.WT_OPEN_LONG
        new_wt_open_long_max = min(cur_wt_open_long+10, 100)
        new_wt_open_long_min = max(cur_wt_open_long-10, -100)
        
        cur_wt_close_long = self.bt.strategy.WT_CLOSE_LONG
        new_wt_close_long_max = min(cur_wt_close_long+10, 100)
        new_wt_close_long_min = max(cur_wt_close_long-10, -10)
        
        # cur_mfi_open_long = self.bt.strategy.MFI_OPEN_LONG
        # new_mfi_open_long_max = min(cur_mfi_open_long+5, 100)
        # new_mfi_open_long_min = max(cur_mfi_open_long-5, -10)
        
        cur_wt_open_short = self.bt.strategy.WT_OPEN_SHORT
        new_wt_open_short_max = min(cur_wt_open_short+10, 100)
        new_wt_open_short_min = max(cur_wt_open_short-10, -100)
        
        cur_wt_close_short = self.bt.strategy.WT_CLOSE_SHORT
        new_wt_close_short_max = min(cur_wt_close_short+10, 10)
        new_wt_close_short_min = max(cur_wt_close_short-10, -100)

        # cur_mfi_open_short = self.bt.strategy.MFI_OPEN_SHORT
        # new_mfi_open_short_max = min(cur_mfi_open_short+5, 40)
        # new_mfi_open_short_min = max(cur_mfi_open_short-5, -40)

        new_wt_open_long_max = -10
        new_wt_open_long_min = -60
        
        new_wt_close_long_max = 60
        new_wt_close_long_min = 10
        
        new_wt_open_short_max = 60
        new_wt_open_short_min = 10
        
        new_wt_close_short_max = -10
        new_wt_close_short_min = -60
        
        def objective(trial):
            self.bt.reset_exchange()

            self.bt.strategy.update_params(
                # wtsma_length = trial.suggest_int('wtsma_length', 100, 200),
                wt_open_long = trial.suggest_uniform('wt_open_long', new_wt_open_long_min, new_wt_open_long_max),
                # wt_close_long = trial.suggest_uniform('wt_close_long', new_wt_close_long_min, new_wt_close_long_max),
                # mfi_open_long = trial.suggest_uniform('mfi_open_long', new_mfi_open_long_min, new_mfi_open_long_max),
                wt_open_short = trial.suggest_uniform('wt_open_short', new_wt_open_short_min, new_wt_open_short_max),
                # wt_close_short = trial.suggest_uniform('wt_close_short', new_wt_close_short_min, new_wt_close_short_max),
                # mfi_open_short = trial.suggest_uniform('mfi_open_short', new_mfi_open_short_min, new_mfi_open_short_max),
            )
            self.bt.strategy.update_indicators()

            self.bt.run_backtest(start_index=0, stop_index=self.split_index)
            self.bt.print_report()
            # return (-1 * self.bt.get_sharpe_ratio())
            # return (-1 * self.bt.get_cross_score())
            return (-1 * self.bt.get_total_realised_pl())

        print(f"Creating Study")
        study = optuna.create_study()
        study.optimize(objective, n_trials=35)

        print()
        print(f"Best params: {study.best_params}")

        print()
        print(f"Updating strategy with best params...")

        self.bt.strategy.update_params(
            # wtsma_length = study.best_params.get('wtsma_length'),
            wt_open_long = study.best_params.get('wt_open_long'),
            # wt_close_long = study.best_params.get('wt_close_long'),
            # mfi_open_long = study.best_params.get('mfi_open_long'),
            wt_open_short = study.best_params.get('wt_open_short'),
            # wt_close_short = study.best_params.get('wt_close_short'),
            # mfi_open_short = study.best_params.get('mfi_open_short'),
        )
        self.bt.strategy.update_indicators()

        print(f"Testing set results...")
        self.bt.reset_exchange()
        self.bt.run_backtest(start_index=0, stop_index=self.split_index)
        self.bt.print_report()

        print(f"Running 'live' trades...")
        self.bt.reset_exchange()
        self.bt.run_backtest(start_index=self.split_index)
        self.bt.print_report()