# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 23:23:57 2022

@author: eborl
"""
from polygon import RESTClient

def config():
    # client = RESTClient() # POLYGON_API_KEY is used
    client = RESTClient("bg56Q7GrGzPpqY4dlzA9spIL3dsGsEL0") # api_key is used
    return client

def store():
    

def get_all_market_one_day(date):
    data = client.get_grouped_daily_aggs(date)
    