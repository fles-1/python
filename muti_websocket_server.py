# -- coding: utf-8 --
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
from tornado import gen
import tornado.process
from tornado.web import url
from together import _websocket_client
from together import bibox_websocket_client
import threading
import time
import asyncio

clients = []  # 客户端列表对象


class serverWsKline(tornado.websocket.WebSocketHandler):
    # websocket的k线数据推送

    @gen.coroutine
    def pushing(self, wsurl, symbol, interval):
        for i in _websocket_client.get_kline(wsurl, symbol, interval):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, wsurl, symbol, interval):
        clients.append(self)
        # gen.sleep(1)
        self.pushing(wsurl, symbol, interval)
        print(clients)
    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self):
        clients.remove(self)


def force_close():
    ''' 单独开启一个线程，每隔5秒判断,request.request_time为对象连接持续的时间
    使用asyncio.new_event_loop函数建立一个新的事件循环，并使用asyncio.set_event_loop设置全局的事件循环，
    这时候就可以多次运行异步的事件循环了，不过最好保存默认的asyncio.get_event_loop并在事件循环结束的时候还原回去 '''

    asyncio.set_event_loop(asyncio.new_event_loop())
    while True:
        time.sleep(5)
        for obj in clients:
            if obj.request.request_time() > 60:
                obj.close()


class serverWsTrade(tornado.websocket.WebSocketHandler):
    # websocket的实时成交信息symbol=btc_usdt
    @gen.coroutine
    def pushing(self, wsurl, symbol):
        for i in _websocket_client.get_trade(wsurl, symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, wsurl, symbol):
        clients.append(self)
        # gen.sleep(1)
        self.pushing(wsurl, symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self):
        clients.remove(self)

class serverWsTicker(tornado.websocket.WebSocketHandler):
    # websocket的前24小时交易对行情
    @gen.coroutine
    def pushing(self, wsurl, symbol):
        for i in _websocket_client.get_ticker(wsurl, symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, wsurl, symbol):
        clients.append(self)
        yield self.pushing(wsurl, symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self) -> None:
        clients.remove(self)

class serverWsDepth(tornado.websocket.WebSocketHandler):
    # websocket的深度盘口
    @gen.coroutine
    def pushing(self, wsurl, symbol, step):
        for i in _websocket_client.get_depth(wsurl, symbol, step):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, wsurl, symbol, step):
        clients.append(self)
        # gen.sleep(1)
        self.pushing(wsurl, symbol, step)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True

    def on_close(self) -> None:
        clients.append(self)

# bibox

class biboxserverWsKline(tornado.websocket.WebSocketHandler):
    # websocket的k线数据推送
    @gen.coroutine
    def pushing(self, symbol, interval):
        for i in bibox_websocket_client.get_kline(symbol, interval):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol, interval):
        # gen.sleep(1)
        self.pushing(symbol, interval)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class biboxserverWsTicker(tornado.websocket.WebSocketHandler):
    # websocket的行情推送
    @gen.coroutine
    def pushing(self, symbol):
        for i in bibox_websocket_client.get_ticker(symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol):
        # gen.sleep(1)
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class biboxserverWsTrade(tornado.websocket.WebSocketHandler):
    # websocket的行情推送
    @gen.coroutine
    def pushing(self, symbol):
        for i in bibox_websocket_client.get_trade(symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol):
        # gen.sleep(1)
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class biboxserverWsDepth(tornado.websocket.WebSocketHandler):
    # websocket的行情推送
    @gen.coroutine
    def pushing(self, symbol):
        for i in bibox_websocket_client.get_depth(symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol):
        # gen.sleep(1)
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            # ws
            url(r'/bix/ws/KlineData/(\w+)/(.*)/(\d+\w+)', serverWsKline),
            url(r'/bix/ws/TickerData/(\w+)/(.*)', serverWsTicker),
            url(r'/bix/ws/TradeData/(\w+)/(.*)', serverWsTrade),
            url(r'/bix/ws/DepthData/(\w+)/(.*)/(\w+\d)', serverWsDepth),
            #
            url(r'/bix/ws/Klinedata/biboxex/(\w+\w+)/(\d+\w+)', biboxserverWsKline),
            url(r'/bix/ws/Tickerdata/biboxex/(\w+\w+)', biboxserverWsTicker),
            url(r'/bix/ws/Tradedata/biboxex/(\w+\w+)', biboxserverWsTrade),
            url(r'/bix/ws/Depthdata/biboxex/(\w+\w+)', biboxserverWsDepth),
        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == '__main__':
    threading.Thread(target=force_close).start()
    app = Application()
    server = HTTPServer(app)
    server.listen(port=8080)
    tornado.ioloop.IOLoop.current().start()
