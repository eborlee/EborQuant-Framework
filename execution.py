# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 22:31:10 2022

@author: eborl
"""
from abc import ABCMeta, abstractmethod
import datetime
import queue

from event import FillEvent, OrderEvent

class ExecutionHandler(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """
        传入一个OrderEvent，并执行，输出一个FillEvent，使其填到Events队列里
        Parameters
        ----------
        event - Order Event

        Returns
        -------

        """
        raise NotImplementedError("Should implement execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):

    def __init__(self, events):
        """
        初始化handler，设置event queues
        Parameters
        ----------
        events - The queue of Event Objects
        """
        self.events = events

    def execute_order(self, event):
        if event.type == "ORDER":
            fill_event = FillEvent(
                datetime.datetime.utcnow(), event.symbol,
                "ARCA", event.quantity, event.direction, None
            )
            # ARCA is just a placeholder
            self.events.put(fill_event)