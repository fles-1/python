# -- coding: utf-8 --
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
import requests
import json
from tornado import gen
import tornado.process
from tornado.web import url
import KuCoin_websocket
from webapi import AOFEX_api
import time

interval_list = ['1min', '5min', '15min', '30min', '60min', '1day', '1mon', '1week', '1year']

def get_symbol():
    symbol_data = requests.get('https://openapi.aofex.com/openApi/market/symbols').text
    for i in json.loads(symbol_data)['result']:
        yield i['symbol']


users = []  # 用来存放在线用户的每个连接的ip


class ConnectHandler(tornado.websocket.WebSocketHandler):


    def check_origin(self, origin):
        # '''重写同源检查 解决跨域问题,True允许跨域'''
        return True

    @gen.coroutine
    def doing(self, symbol, interval):
        try:
            while True:
                time.sleep(1)
                if symbol in [x for x in get_symbol()]:
                    if interval in interval_list:
                        yield self.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', symbol, interval))

        except Exception as e:
            print(e)
        #raise gen.Return('no blocking')

    @gen.coroutine
    def open(self, symbol, interval):
        users.append(self.request.remote_ip)
        print("在线用户ip列表%s" % users)
        yield self.doing(symbol, interval)

    def on_close(self):
        # '''websocket连接关闭后被调用'''
        print("用户%s离开" % self.request.remote_ip)

    def on_message(self, message):
        # '''接收到客户端消息时被调用,必须重写此方法'''
        print(message)


class C5Handler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        while True:
            time.sleep(1)
            self.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', 'BTC-USDT', '5min'))


class CucoinHandler(tornado.websocket.WebSocketHandler):
    # 使用websocket推送本身是一个循环进程，不需要while循环
    def open(self, symbol, *args, **kwargs):
        for i in KuCoin_websocket.kucoin(symbol):
            self.write_message(i)
    def on_message(self, message):

        print(message)
        # time.sleep(1)



class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("websocket start")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            #(r'/index', MainHandler),
            url(r'/bix/ws/klineData/aofex/(\w+-\w+)/(\d+\w+)', ConnectHandler,  name="aofexurl"),
            url(r'/bix/ws/klineData/kucoin/(\w+-\w+)', CucoinHandler)
        ]
        tornado.web.Application.__init__(self, handlers)




if __name__ == "__main__":
    app = Application()
    server = HTTPServer(app)
    server.listen(port=8080)
    tornado.ioloop.IOLoop.current().start()
