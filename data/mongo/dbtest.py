# -*- coding: utf-8 -*-
"""
Created on Wed Oct 26 23:08:00 2022

@author: eborl
"""

import mongoCollection as mc

collection = mc.get_collection("mytestdb","testset")

collection.insert_one({"name":"zhangsan","age":19}) 
