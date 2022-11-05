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

    def update_fill(self, event):
        """
        调用上面两个update方法来更新postions和holdings
        Parameters
        ----------
        event

        Returns
        -------

        """
        if event.type == "FILL":
            self.update_holdings_from_fill(event)
            self.update_positions_from_fill(event)


    def generate_naive_order(self, signal):
        """
        portfolio不仅要处理FillEvents， 还要处理OrderEvents（一经收到SignalEvents）
        之所以叫naive是因为没有风控考量，信号发出就直接执行某个仓位比例的交易动作
        Parameters
        ----------
        signal

        Returns
        -------

        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        strength = signal.strength

        mkt_quantity = 100
        cur_quantity = self.current_positions[symbol]
        order_type = "MKT"

        if direction == "LONG" and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == "SHORT" and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')
        if direction == "EXIT" and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(mkt_quantity), 'SELL')
        if direction == "EXIT" and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(mkt_quantity), 'BUY')

        return order


    def update_ginal(self, event):
        if( event.type == "SIGNAL"):
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)

    def create_equity_curve_dataframe(self):

        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace = True)
        curve['return'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0+curve['returns']).cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252*60*6.5)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1)*100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.equity_curve.to_csv("equity.csv")
        return stats