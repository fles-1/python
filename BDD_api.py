# -- coding: utf-8 --

import requests


def get_allticker():
    # 获取所有交易行情
    url = 'https://openapi.hiex.pro/open/api/get_allticker'
    data = requests.get(url).text
    # print(data)
    return data


def get_kline(symbol, interval):
    # 获取k线数据symbol=btcusdt,interval=1
    url = 'https://openapi.hiex.pro/open/api/get_records?symbol=%s&period=%s' % (symbol, interval)
    data = requests.get(url).text
    # print(data)
    return data


def get_dept(symbol, dept_type):
    # 查询买卖盘深度,symbol=btcusdt,dept_type=dept0 |1 |2
    url = 'https://openapi.hiex.pro/open/api/market_dept?symbol=%s&type=%s' % (symbol, dept_type)
    data = requests.get(url).text
    # print(data)
    return data


def get_trades(symbol):
    # 获取行情成交记录,symbol=btcusdt
    url = 'https://openapi.hiex.pro/open/api/get_trades?symbol=%s' % symbol
    data = requests.get(url).text
    # print(data)
    return data
