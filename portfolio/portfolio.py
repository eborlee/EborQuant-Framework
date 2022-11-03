# -*- coding: utf-8 -*-


import datetime
from math import floor

import queue

import numpy as np
import pandas as pd

from event import FillEvent, OrderEvent
from portfolio.performance import create_sharpe_ratio, create_drawdowns

class Portfolio(object):
    

    def __init__(self, bars, events, start_date, initial_capital=100000.0):
        """
        

        Parameters
        ----------
        bars : TYPE
            The DataHandler object with current market data
        events : TYPE
            事件队列
        start_date : TYPE
            DESCRIPTION.
        initial_capital : TYPE, optional
            DESCRIPTION. The default is 100000.0.

        Returns
        -------
        None.

        """
        self.bars = bars
        self.events = events # 事件队列
        self.symbol_list = self.bars.symbol_list # 股票列表
        self.start_date = start_date
        self.initial_capital = initial_capital
        
        
        self.all_positions = self.construct_all_positions() # 历史记录？[]
        
        # 初始化仓位 所有股票均为0股
        self.current_positions = dict( (k,v) for k,v in \
                                      [(s,0) for s in self.symbol_list])
            
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
            
        
    def construct_all_positions(self):
        """
        

        Returns
        -------
        None.

        """
        d = dict( (k,v) for k,v in [(s,0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        return [d]
    
    
    def construct_all_holdings(self):
        """
        

        Returns
        -------
        None.

        """
        d = dict( (k,v) for k,v in [(s,0) for s in self.symbol_list])
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commision'] = 0.0
        d['total'] = self.initial_capital
        return [d]
    
    
    def construct_current_holdings(self):
        """
        

        Returns
        -------
        None.

        """
        d = dict( (k,v) for k,v in [(s,0) for s in self.symbol_list])
        d['cash'] = self.initial_capital
        d['commision'] = 0.0
        d['total'] = self.initial_capital
        return d
    
    def update_timeindex(self, event):
        """

        Parameters
        ----------
        event: MarketEvent

        Returns
        -------

        """
        latest_datetime = self.bars.get_latest_bar_time(
            self.symbol_list[0]
        )

        # update positions
        #
