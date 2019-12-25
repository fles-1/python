# -- coding: utf-8 --
import websocket
import gzip
import json
import time
import re
import requests

# 各交易所ws字典对象，用于获取socket数据
dict_ws = {
    'abqqex': 'wss://ws.abby.global/kline-api/ws', 'btsgex': 'wss://ws.bitsg.com/kline-api/ws',
    'bddex': 'wss://ws.bddex.io/kline-api/ws', 'bikiex': 'wss://ws.biki.com/kline-api/ws',
    'bzex': 'wss://ws.bzex.co/kline-api/ws', 'dxdex': 'wss://ws.dxdcoin.com/kline-api/ws',
    'imoex': 'wss://ws.imoex.top/kline-api/ws', 'wbfex': 'wss://ws.wbf.io/kline-api/ws',
    'momoex': 'wss://ws.momoex.com/kline-api/ws', 'gokoex': 'wss://ws.goko.com/kline-api/ws',
    'btboex': 'wss://ws.btbo.com/kline-api/ws', 'bbkxex': 'wss://ws.bbkx.com/kline-api/ws',
    'hkex.oneex': 'wss://ws.hkex.one/kline-api/ws', 'biiitex': 'wss://ws.biiit.com/kline-api/ws',
    'ffex': 'wss://ws.ffex.pro/kline-api/ws'}

# 各交易所api字典对象，用于获取交易所所有交易对
dict_api = {
    'abqqex': 'https://openapi.abby.global/open/api/common/symbols',
    'btsgex': 'https://openapi.bitsg.com/open/api/common/symbols',
    'bddex': 'https://openapi.bddex.io/open/api/common/symbols',
    'bikiex': 'https://openapi.biki.com/open/api/common/symbols',
    'bzex': 'https://openapi.bzex.co/open/api/common/symbols',
    'dxdex': 'https://openapi.dxdcoin.com/open/api/common/symbols',
    'imoex': 'https://openapi.imoex.top/open/api/common/symbols',
    'wbfex': 'https://openapi.wbf.io/open/api/common/symbols',
    'momoex': 'https://openapi.momoex.com/open/api/common/symbols',
    'gokoex': 'https://openapi.goko.com/open/api/common/symbols',
    'btboex': 'https://openapi.btbo.com/open/api/common/symbols',
    'bbkxex': 'https://openapi.bbkx.com/open/api/common/symbols',
    'hkex.oneex': 'https://openapi.hkex.one/open/api/common/symbols',
    'biiitex': 'https://openapi.biiit.com/open/api/common/symbols',
    'ffex': 'https://openapi.ffex.pro/open/api/common/symbols'}


def get_symbol(api):
    res = requests.get(api).text
    data_dict = json.loads(res)
    return data_dict['data']


def get_kline(url_ws, symbol, interval):
    # 获取websocket的k线symbol=btcusdt,interval=1min
    ws = websocket.WebSocket()
    interval_ = re.compile(r'\D+').findall(interval)[0].upper() + re.compile(r'\d+').findall(interval)[0]
    try:
        ws.connect(dict_ws[url_ws])
        if symbol == "*":
            for d in get_symbol(dict_api[url_ws]):
                ws.send(
                    '{"event":"sub","params":{"channel":"market_%s_kline_%s","cb_id":1001}}' % (d['symbol'], interval))
        else:
            symbol_list = symbol.split(',')
            for d in symbol_list:
                ws.send(
                    '{"event":"sub","params":{"channel":"market_%s_kline_%s","cb_id":1001}}' % (d, interval))
    except Exception as e:
        print(e)
    while True:
        result = ws.recv()
        data = gzip.decompress(result).decode('utf8')
        if 'ping' in json.loads(data):
            ws.send(json.dumps({"pong": json.loads(data)["ping"]}))
        else:
            data = json.loads(data)
            data_channel = data['channel']
            sym = data_channel[7:][:data_channel[7:].find('_')]
            data['data'] = data.pop('tick')

            data['data']['volume'] = data['data'].pop('vol')
            time_array = time.strptime(data['data']['ds'], "%Y-%m-%d %H:%M:%S")
            del data['data']['id']
            del data['data']['tradeId']
            del data['data']['ds']
            timestamp = int(time.mktime(time_array))
            data['data']['timestamp'] = timestamp
            data['data']['count'] = 0
            dic = {"data": data["data"]}

            last_data = {"data": dic, "interval": interval_, "symbol": sym, "rate": 0, "timestamp": data['ts']}
            yield json.dumps(last_data)
            # yield data
# for i in get_kline('abqqex', 'btc_usdt','1min'):
#     print(i)


def get_ticker(url_ws, symbol):

    # 获取websocket的前24小时交易对行情symbol=btcusdt
    ws = websocket.WebSocket()
    try:
        ws.connect(dict_ws[url_ws])
        if symbol == "*":
            for d in get_symbol(dict_api[url_ws]):
                ws.send('{"event":"sub","params":{"channel":"market_%s_ticker","cb_id":1001}}' % d['symbol'])
        else:
            symbol_list = symbol.split(',')
            for d in symbol_list:
                ws.send('{"event":"sub","params":{"channel":"market_%s_ticker","cb_id":1001}}' % d)

    except Exception as e:
        print(e)
    while True:
        result = ws.recv()
        data = gzip.decompress(result).decode('utf8')
        if 'ping' in json.loads(data):
            ws.send(json.dumps({"pong": json.loads(data)["ping"]}))
        else:
            data = json.loads(data)
            data_channel = data['channel']
            sym = data_channel[7:][:data_channel[7:].find('_')]
            data['data'] = data.pop('tick')
            data['data']['volume'] = data['data'].pop('vol')
            dic = {"data": data["data"]}

            data = {"data": dic,  "symbol": sym, "rate": 0, "timestamp": data['ts']}
            yield json.dumps(data)
# for i in get_ticker("abqqex", "btcusdt"):
#     print(i)


def get_trade(url_ws, symbol):
    # 获取websocket的实时成交信息symbol=btc_usdt
    ws = websocket.WebSocket()
    try:
        ws.connect(dict_ws[url_ws])
        if symbol == "*":
            for d in get_symbol(dict_api[url_ws]):
                ws.send('{"event":"sub","params":{"channel":"market_%s_trade_ticker","cb_id":1001}}' % d['symbol'])
        else:
            symbol_list = symbol.split(',')
            for d in symbol_list:
                ws.send('{"event":"sub","params":{"channel":"market_%s_trade_ticker","cb_id":1001}}' % d)

    except Exception as e:
        print(e)
    while True:
        result = ws.recv()
        data = gzip.decompress(result).decode('utf8')
        if 'ping' in json.loads(data):
            ws.send(json.dumps({"pong": json.loads(data)["ping"]}))
        else:
            data = json.loads(data)
            data_channel = data['channel']
            sym = data_channel[7:][:data_channel[7:].find('_')]
            for v in data['tick']["data"]:
                # print(v)
                del v["ds"]
                del v["vol"]
                v["direction"] = v.pop("side")
                v["timestamp"] = v.pop("ts")
                v["tradeId"] = v.pop("id")
            da = {"data": {"symbol": sym, "timestamp": data["ts"], "rate": 0, "tradeList": data["tick"]["data"]}}
            yield json.dumps(da)
            # yield data
# for i in get_trade('abqqex', 'btcusdt'):
#     print(i)


def get_depth(url_ws, symbol, step):
    # 获取websocket的深度盘口symbol=btc_usdt,step=step0 |1 |2
    ws = websocket.WebSocket()
    try:
        ws.connect(dict_ws[url_ws])
        if symbol == "*":
            for d in get_symbol(dict_api[url_ws]):
                ws.send('{"event":"sub","params":{"channel":"market_%s_depth_%s","cb_id":1001}}' % (d['symbol'], step))
        else:
            symbol_list = symbol.split(',')
            for d in symbol_list:
                ws.send('{"event":"sub","params":{"channel":"market_%s_depth_%s","cb_id":1001}}' % (d, step))

    except Exception as e:
        print(e)
    while True:
        result = ws.recv()
        data = gzip.decompress(result).decode('utf8')
        # print(data)
        if 'ping' in json.loads(data):
            # print(json.dumps({"pong": json.loads(data)["ping"]}))
            ws.send(json.dumps({"pong": json.loads(data)["ping"]}))
        else:
            data = json.loads(data)
            data_channel = data['channel']
            sym = data_channel[7:][:data_channel[7:].find('_')]
            lis_asks = []
            lis_bids = []
            for v in data['tick']['asks']:
                x = {"amount": v[1], "price": v[0]}
                lis_asks.append(x)
                data['tick']['asks'] = x
            for v in data['tick']['buys']:
                x = {"amount": v[1], "price": v[0]}
                data['tick']['buys'] = x
                lis_bids.append(x)
            da = {"data": {"data": {"asks": lis_asks, "bids": lis_bids, "timestamp": time.time()}, "symbol": sym,
                           "timestamp": time.time(), "type": step, "rate": 0}}
            yield json.dumps(da)
            # yield data

# for i in get_depth("btcusdt", "step0"):
#     print(i)
