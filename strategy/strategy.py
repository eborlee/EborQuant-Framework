# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 22:31:10 2022

@author: eborl
"""

# from __future__ import print_function

from abc import ABCMeta, abstractmethod
import datetime
import queue
import numpy as np
import pandas as pd

from event import SignalEvent

class Strategy(object):
    
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def calculate_signals(self):
        
        raise NotImplementedError("Should implement calculate_signals()")

