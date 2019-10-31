# -- coding: utf-8 --
import websocket
import gzip
import zlib
import base64
import json
import io
import time

ws = websocket.WebSocket()

try:
        #ws.connect("wss://api.huobi.vn/ws")
        #print(ws)
    #ws.connect('wss://okexcomreal.bafang.com:10442/ws/v3?_compress=false')
    ###ws.connect('ws://192.168.0.88:8080/bix/ws/klineData/huobi/btcusdt/1min')
    ws.connect('ws://127.0.0.1:8080/bix/ws/klineData/kucoin/')
    #ws.connect('wss://fx-ws-testnet.gateio.ws/v4/ws')
    # ws.connect('wss://push-private.kcs.top/endpoint?token=2neAiuYvAU61ZDXANAGAsiL4-iAExhsBXZxftpOeh_55i3Ysy2q2LEsEWU64md'
    #            'zUOPusi34M_wGoSf7iNyEWJ_MNZX9UK36jyO1GeT1iyt5clLvBIvt6QtiYB9J6i9GjsxUuhPw3BlrzazF6ghq4L06w2kLv0trGG'
    #            'rUo6KMHOOs=.bZJvhtk_Gl-iVkYOJMJDOA==&acceptUserMessage=true')
except Exception as e:
    print('异常：', e)
#8riRjJ6H6e
#print('OK')
def inflate(data):
    decompress = zlib.decompressobj(
            -zlib.MAX_WBITS  # see above
    )
    inflated = decompress.decompress(data)
    inflated += decompress.flush()
    return inflated
#req = '{"time" : 123456, "channel" : "futures.tickers", "event": "subscribe", "payload" : ["BTC_USD"]}'
#req = '{"id":1545910660739,"type":"subscribe","topic":"/market/ticker:BTC-USDT","response":true}'


req = '{"symbol":"VDS_USDT","interval":"Min1"}'
ws.send(req)
while True:

    #req = '{ "sub": "market.ethbtc.kline.1min", "id": "id1" }'

    resp = ws.recv()
    print(resp)

    #print(inflate(resp).decode())
    #print(resp)
# from websocket import create_connection
# ws = create_connection("wss://fx-ws-testnet.gateio.ws/v4/ws")
# ws.send('{"time" : 123456, "channel" : "futures.tickers", "event": "subscribe", "payload" : ["BTC_USD"]}')
# print(ws.recv())
