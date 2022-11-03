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
        
        # positions仅仅记录持仓股票代码和股票数量
        self.all_positions = self.construct_all_positions() # 历史记录？[]
        
        # 初始化仓位 所有股票均为0股
        self.current_positions = dict( (k,v) for k,v in \
                                      [(s,0) for s in self.symbol_list])

        # holdings记录整个仓位的详细数据
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
·       我的理解是，由市场数据更新所引起的持仓价值变化的处理
        Parameters
        ----------
        event: MarketEvent

        Returns
        -------

        """
        latest_datetime = self.bars.get_latest_bar_time(
            self.symbol_list[0]
        )

        # update holdings
        dh = dict( (k,v) for k, v in [(s,0) for s in self.symbol_list])
        dh['datetime'] = latest_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']


        for s in self.symbol_list:
            # 近似real value
            market_value = self.current_positions[s] * self.bars.get_latest_bar(s, "adj_close")
            dh[s] = market_value
            dh['total'] += market_value

        # append the current holdings 添加到holdings的历史记录？
        self.all_holdings.append(dh)

    def update_positions_from_fill(self, fill):
        """
        交易事件引起的持仓情况变化
        Parameters
        ----------
        fill

        Returns
        -------

        """
        fill_direction = 0
        if fill.direction == "BUY":
            fill_direction = 1
        if fill.direction == "SELL":
            fill_direction = -1

        # update positions list with new quantities
        self.current_positions[fill.symbol] += fill_direction * fill.quantity

    def update_holdings_from_fill(self, fill):
        """

        Parameters
        ----------
        fill

        Returns
        -------

        """
        fill_direction = 0
        if fill.direction == "BUY":
            fill_direction = 1
        if fill.direction == "SELL":
            fill_direction = -1

        fill_cost = self.bars.get_latest_bar_value(fill.symbol, "adj_close") # 没懂这里为什么fillcost不直接从fillevent里拿
        # 书里的解释是说 为了模拟填充成本，在回测环境中并不能直到市场冲击和交易簿的深度，所以要使用当前市场价格作为一个近似估计
        # 我的理解是 回测中，信号产生传过来，创建了fillevent，但不能真正做到模拟真实的成交，多少股在多少价位balabala
        # 那么问题来了，fillevent中fillcost就不是这个latestbar吗？看看后面怎么调用的

        cost = fill_direction * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        # self.current_holdings['total'] -= (cost + fill.commission) # ?这total怎么会要减掉成本
        self.current_holdings['total'] -= fill.commission


