# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 22:31:10 2022

@author: eborl
"""

import datetime
import queue
import time

class Backtest(object):

    def __init__(
            self, csv_dir, symbol_list, initial_capital,
            heartbeat, start_date, data_handler,
            execution_handler, portfolio, strategy
    ):
        """

        Parameters
        ----------
        csv_dir
        symbol_list
        initial_capital
        heartbeat
        start_date
        data_handler
        execution_handler
        portfoliom
        strategy
        """
        self.csv_dir = csv_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_cls = portfolio
        self.strategy_cls = strategy
        self.events = queue.Queue()

        self.signals    = 0
        self.orders     = 0
        self.fills      = 0
        self.num_strats = 1

        self._generate_trading_instances()

    def _generate_trading_instances(self):

        print("Creating DataHandler, Strategy, Portfolio and ExecutionHandler")

        self.data_handler = self.data_handler_cls(self.events, self.csv_dir, self.symbol_list)
        self.strategy = self.strategy_cls(self.data_handler, self.events)
        self.portfolio = self.portfolio_cls(self.data_handler, self.events,
                                            self.start_date,
                                            self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.events)

    def _run_backtest(self):
        """

        Returns
        -------

        """
        i = 0
        while True:
            i += 1
            print(i)
            # update the market bars
            if self.data_handler.continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break

            # handle the events
            while True:
                try:
                    event = self.events.get(False) # 队列方法
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == 'MARKET':
                            self.strategy.calculate_signals(event)
                            self.portfolio.update_timeindex(event)

                        elif event.type == 'SIGNAL':
                            self.signals += 1

