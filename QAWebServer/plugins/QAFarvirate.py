from QUANTAXIS.QAUtil import (DATABASE)
import numpy
import pandas as pd
from pandas import DataFrame


# PyMongo:https://www.cnblogs.com/nixingguo/p/7260604.html

def QA_add_stock_fav(code, collections=DATABASE.stock_fav):
    stock_fav = {
        'code': code
    }
    temp = collections.find(stock_fav)
    if temp.count() == 0:
        collections.insert(stock_fav)
        return 1
    else:
        return 0


def QA_delete_stock_fav(code, collections=DATABASE.stock_fav):
    stock_fav = {
        'code': code
    }
    temp = collections.find(stock_fav)
    if temp.count() == 0:
        return 0
    else:
        collections.remove(stock_fav)
        return 1


def QA_fetch_stock_fav(collections=DATABASE.stock_fav):
    result = collections.find()
    if result.count() == 0:
        return pd.DataFrame({'code': ['000002']}).set_index('code', drop=False)
    else:
        return pd.DataFrame([item for item in result]).drop('_id', axis=1, inplace=False).set_index('code', drop=False)
