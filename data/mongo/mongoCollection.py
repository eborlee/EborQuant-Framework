# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 23:00:57 2022

@author: eborl
"""

import mongoConnect

def get_collection(db_name, collection_name):
    
    db = mongoConnect.connect(db_name);
    
    collection = db[str(collection_name)]   # 没有则自动创建
    
    return collection
    
    