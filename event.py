# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 23:18:45 2022

@author: eborl
"""

class Event(object):
    """
    Event is base class providing an interface for all subsequent 
    (inherited) events, that will trigger further events in the 
    trading infrastructure.   
    """
    pass

class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars
    """
    
    def __init__(self):
        """
        Initialises the MarketEvent

        Returns
        -------
        None.

        """
        self.type = 'MARKET'
        
class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a strategy object.
    This is received by a portfolio object and acted upon
    """
    def __init__(self, strategy_id, symbol, datetime, signal_type, strength):
        """
        Initialises the SignalEvent

        Parameters
        ----------
        symbol : TYPE
            stock code
        datetime : TYPE
            The timestamp at which the signal was generated
        signal_type : TYPE
            Long or Short
        strength:
            Adjustment factor "suggestion" used to scale quantity at the portfolio level.
            Userful for pairs strategies

        Returns
        -------
        None.

        """
        self.type = "SIGNAL"
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strategy_id = strategy_id
        self.strength = strength
        
class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction
    """
    def __init__(self, symbol, order_type, quantity, direction):
        """
        

        Parameters
        ----------
        symbol : TYPE
            DESCRIPTION.
        order_type : TYPE
            DESCRIPTION.
        quantity : TYPE
            DESCRIPTION.
        direction : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        
        self.type = "ORDER"
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):

        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
              (self.symbol, self.order_type, self.quantity, self.direction))
        
class FillEvent(Event):
    """
    完成的订单事件
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    acutally filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """
    def __init__(self, timeindex, symbol, exchange, quantity,
                 direction, fill_cost, commission=None):
        """
        
        当FillEvent被创建出来的时候就已经初始化好了这些 股票代码、方向、数量、交易费用等等 并传给其他层
        Parameters
        ----------
        timeindex : TYPE
            DESCRIPTION.
        symbol : TYPE
            DESCRIPTION.
        exchange : TYPE
            DESCRIPTION.
        quantity : TYPE
            DESCRIPTION.
        direction : TYPE
            DESCRIPTION.
        fill_cost : TYPE
            DESCRIPTION.
        commission : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.type = "FILL"
        self.timeindex = timeindex
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction # 交易方向 1 0 -1
        self.fill_cost = fill_cost
        
        # Calculate commision
        if commission is None:
            self.commision = self.calulate_ib_commission()
        else:
            self.commission = commission
            
    def calulate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API, in USD
        
        This does not include exchange or ECN fees.

        Returns
        -------
        None.

        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:
            full_cost = max(1.3, 0.008 * self.quantity)
        full_cost = min(full_cost, 0.5 / 100.0 * self.quantity * self.fill_cost)
        return full_cost
        
        
        