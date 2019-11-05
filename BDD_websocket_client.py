# -- coding: utf-8 --
import websocket
import gzip
import json


def get_kline(symbol, interval):
    # 获取币多多websocket的k线symbol=btcusdt,interval=1min
    ws = websocket.WebSocket()
    try:
        ws.connect('wss://ws.bddex.io/kline-api/ws')
        ws.send('{"event":"sub","params":{"channel":"market_%s_kline_%s","cb_id":1001}}' % (symbol, interval))
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
            yield data


def get_ticker(symbol):
    # 获取币多多websocket的前24小时交易对行情symbol=btcusdt
    ws = websocket.WebSocket()
    try:
        ws.connect('wss://ws.bddex.io/kline-api/ws')
        ws.send('{"event":"sub","params":{"channel":"market_%s_ticker","cb_id":1001}}' % symbol)
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
            yield data


def get_trade(symbol):
    # 获取币多多websocket的实时成交信息symbol=btcusdt
    ws = websocket.WebSocket()
    try:
        ws.connect('wss://ws.bddex.io/kline-api/ws')
        ws.send('{"event":"sub","params":{"channel":"market_%s_trade_ticker","cb_id":1001}}' % symbol)
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
            yield data


def get_depth(symbol, step):
    # 获取币多多websocket的深度盘口symbol=btcusdt,step=step0 |1 |2
    ws = websocket.WebSocket()
    try:
        ws.connect('wss://ws.bddex.io/kline-api/ws')
        ws.send('{"event":"sub","params":{"channel":"market_%s_depth_%s","cb_id":1001}}' % (symbol, step))
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
            yield data
