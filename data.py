# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 23:14:12 2022

@author: eborl
"""

import datetime
import os, os.path
import pandas as pd
import numpy as np
from abc import ABCMeta, abstractmethod

from event import MarketEvent



class DataHandler(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
        """
        Returns the last N bars from the latest_symbol list,
        or fewer if less bars are available.
        """
        raise NotImplementedError("Should implement get_latest_bars()")
        
    @abstractmethod
    def get_latest_bar(self, symbol):
        
        raise NotImplementedError("Should implement get_latest_bar()")
        
    @abstractmethod
    def update_bars(self):
        """
        Pushes trhe latest bar to the latest symbol structure for all
        symbols in the symbol list.
        """
        raise NotImplementedError("Should implement update_bars()")
        
    @abstractmethod
    def get_latest_bar_value(self, symbol, val_type):
        
        raise NotImplementedError("Should implement get_latest_bar_value")
        
    @abstractmethod
    def get_latest_bar_values(self, symbol, val_type, N=1):
        
        raise NotImplementedError("Should implement get_latest_bar_values")
        
    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        
        raise NotImplementedError("Should implement get_latest_bar_datetime")

class HistoricCSVDataHandler(DataHandler):
    """
    该类继承自DataHandler基类，用来读取本地磁盘上每个股票的CSV文件，
    并提供一个接口来获得“最新的” Bar， 其方式与实时交易接口相同
    """
    
    def __init__(self, events, csv_dir, symbol_list):
        """
        初始化来请求CSV文件的路径和股票列表
        文件名格式 ： ’symbol.csv‘
        symbol是股票列表中的字符串

        Parameters
        ----------
        events : TYPE
            事件队列
        csv_dir : TYPE
            DESCRIPTION.
        symbol_list : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        self.events = events
        self.CSV_dir = csv_dir
        self.symbol_list = symbol_list
        
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        
        self._open_convert_CSV_files() # 该方法负责处理文件打开
        
    def _open_convert_csv_files(self): # 私有方法
        """
        

        Returns
        -------
        None.

        """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.io.parsers.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s), 
                header=0, index_col=0,
                names=['datetime','open','low','high','close','volume','oi']
                )
        
            if comb_index is None: # 我理解是我以前的calendar的作用？
                comb_index = self.symbol_data[s].index_col
            else:
                comb_index.union(self.symbol_data[s].index) # 取并集
                
            self.latest_symbol_data[s] = []
            
        for s in self.symbol_list:
            # 对每个股票的dataframe的索引用calendar进行重置，并且使用向下填充来填充那些NaN
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()
                
                
            
    def _get_new_bar(self, symbol):
        """
        返回一个最新的bar，以tuple的形式
        (symbol, datetime, open, low, high ,close, volume)
        Parameters
        ----------
        symbol : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        for b in self.symbol_data[symbol]:
            # yield tuple([symbol, datetime.datetime.strftime(b[0], '%Y-%m-%d %H:%M:%S'),
            #              b[1][0], b[1][1], b[1][2], b[1][3], b[1][4]])
            yield b
            
    def get_latest_bar(self, symbol):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Invalid symbol")
            raise
        else:
            return bars_list[-1]
    
    
    def get_latest_bars(self, symbol, N=1):
        """
        从latest_symbol list中返回 N 个bar或 N-K 个 （如果不足）

        Parameters
        ----------
        symbol : TYPE
            DESCRIPTION.
        N : TYPE, optional
            DESCRIPTION. The default is 1.

        Returns
        -------
        None.

        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("That symbol is not available in the hist dataset")
        else:
            return bars_list[-N:]
    
    def update_bars(self):
        """
        将最新的bar加入到 latest_symbol_data中，对于所有的symbols

        Returns
        -------
        None.

        """
        for s in self.symbol_list:
            try:
                bar = self._get_new_bar(s).next
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
        self.events.put(MarketEvent())
        
    def get_latest_bar_datetime(self, symbol):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Invalid symbol")
            raise
        else:
            return bars_list[-1][0]
        
    def get_latest_bar_value(self, symbol, val_type):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Invalid symbol")
            raise
        else:
            return getattr(bars_list[-1][1], val_type)
        
    
    def get_latest_bar_values(self, symbol, val_type, N=1):
        try:
            bars_list = self.get_latest_bars(symbol, N)
        except KeyError:
            print("Invalid symbol")
            raise
        else:
            return np.array([getattr(b[1], val_type) for b in bars_list])
        
        
    
    
    
    
    
    
    
    