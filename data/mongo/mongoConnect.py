# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 22:53:21 2022

@author: eborl
"""


from pymongo import MongoClient
# import socket

def connect(db_name):
    
    # 函数 gethostname() 返回当前正在执行 Python 的系统主机名
    # host = socket.gethostbyname(socket.gethostname())
    
    # 创建连接
    client = MongoClient('mongodb://localhost:27017/')
    db = client[str(db_name)]
    
    return db
    
    
    
