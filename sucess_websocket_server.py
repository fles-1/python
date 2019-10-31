# -- coding: utf-8 --
import tornado.ioloop
import tornado.web
import tornado.websocket
import KuCoin_api
import KuCoin_websocket
from webapi import AOFEX_api
import time


class ConnectHandler(tornado.websocket.WebSocketHandler):

    def check_origin(self, origin):
        # '''重写同源检查 解决跨域问题'''
        return True

    def open(self):
        # '''新的websocket连接后被调动'''
        # self.write_message('Welcome')
        pass

    def on_close(self):
        # '''websocket连接关闭后被调用'''
        pass

    def on_message(self, message):
        # '''接收到客户端消息时被调用'''
        while True:
            time.sleep(1)
            self.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', 'BTC-USDT', '1min'))  # 向客服端发送
class C5Handler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        while True:
            time.sleep(1)
            self.write_message(AOFEX_api.AOFEXAPI().get_kline('kline', 'BTC-USDT', '5min'))

class CkHandler(tornado.websocket.WebSocketHandler):

    def on_message(self, message):
        while True:
            # time.sleep(1)
            self.write_message(KuCoin_websocket.kucoin())

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello world")


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/index', MainHandler),
            (r'/bix/ws/klineData/aofex/btcusdt/1min', ConnectHandler),
            (r'/bix/ws/klineData/aofex/btcusdt/5min', C5Handler),
            (r'/bix/ws/klineData/kucoin/', CkHandler)
        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    app = Application()
    app.listen(8080)
    tornado.ioloop.IOLoop.current().start()
