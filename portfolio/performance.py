# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 22:37:06 2022

@author: eborl
"""

import numpy as np
import pandas as pd

def create_sharpe_ratio(returns, periods=252):
    
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(pnl):
    """
    

    Parameters
    ----------
    pnl : Pandas Series %Return
        DESCRIPTION.

    Returns
    -------
    None.

    """
    # High Water Mark
    hwm = [0] 
    
    idx = pnl.index
    drawdown = pd.Series(index = idx)
    duration = pd.Series(index = idx)
    
    # Loop over the index range
    for t in range(1, len(idx)):
        hwm.append(max(hwm[t-1], pnl[t]))
        drawdown[t] = hwm[t] - pnl[t]
        duration[t] = 0 if drawdown[t] == 0 else duration[t-1] + 1
    return drawdown, drawdown.max(), duration.max()
    


