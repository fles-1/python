# -- coding: utf-8 --
import tornado.ioloop
import tornado.web
import tornado.websocket
import requests
import json
import KuCoin_api
from tornado.web import url
import KuCoin_websocket
from webapi import AOFEX_api
import time

interval_list = ['1min', '5min', '15min', '30min', '60min', '1day', '1mon', '1week', '1year']


def get_symbol():
    symbol_data = requests.get('https://openapi.aofex.com/openApi/market/symbols').text
    for i in json.loads(symbol_data)['result']:
        yield i['symbol']


class ConnectHandler(tornado.websocket.WebSocketHandler):
    users = set()  # 用来存放在线用户的容器

    def check_origin(self, origin):
        # '''重写同源检查 解决跨域问题,允许跨域'''
        return True

    def open(self, symbol, interval, *args, **kwargs):
        # '''新的websocket连接后被调动'''
        # self.write_message('Welcome')

        self.users.add(self)  # 建立连接后添加用户到容器中
        for u in self.users:
            try:
                while True:
                    time.sleep(1)
                    if symbol in [x for x in get_symbol()]:
                        if interval in interval_list:
                            u.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', symbol, interval))  # 向客服端发送
            except Exception as e:
                print(e)

    def on_close(self):
        # '''websocket连接关闭后被调用'''
        self.users.remove(self)  # 用户关闭连接后从容器中移除用户
        print(self.users)

    def on_message(self, message):
        # '''接收到客户端消息时被调用,必须重写此方法'''
        print(message)


class C5Handler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        while True:
            time.sleep(1)
            self.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', 'BTC-USDT', '5min'))


class CkHandler(tornado.websocket.WebSocketHandler):
    # 使用websocket推送本身是一个循环进程，不需要while循环
    def on_message(self, message):

        print(message)
        # time.sleep(1)
        for i in KuCoin_websocket.kucoin():
            self.write_message(i)


class MainHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("websocket start")


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r'/index', MainHandler),
            url(r'/bix/ws/klineData/aofex/(\w+-\w+)/(\d+\w+)', ConnectHandler,  name="b1url"),
            (r'/bix/ws/klineData/kucoin/', CkHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    app = Application()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
