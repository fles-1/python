# -- coding: utf-8 --
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
from tornado import gen
import tornado.process
from tornado.web import url
from BDDex import BDD_api
from BDDex import BDD_websocket_client


class BDDserverApiAllticker(tornado.websocket.WebSocketHandler):
    # 币多多api所有交易行情推送
    @gen.coroutine
    def pushing(self):
        while True:
            gen.sleep(5)
            yield self.write_message(BDD_api.get_allticker())

    @gen.coroutine
    def open(self):
        self.pushing()

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverApiKline(tornado.websocket.WebSocketHandler):
    # 币多多api的k线推送
    @gen.coroutine
    def pushing(self, symbol, interval):
        while True:
            gen.sleep(2)
            yield self.write_message(BDD_api.get_kline(symbol, interval))

    @gen.coroutine
    def open(self, symbol, interval):
        self.pushing(symbol, interval)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverApiDept(tornado.websocket.WebSocketHandler):
    # 币多多api查询买卖盘深度
    @gen.coroutine
    def pushing(self, symbol, dept):
        while True:
            gen.sleep(2)
            yield self.write_message(BDD_api.get_dept(symbol, dept))

    @gen.coroutine
    def open(self, symbol, dept):
        self.pushing(symbol, dept)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverApiTrades(tornado.websocket.WebSocketHandler):
    # 币多多api行情单个交易对成交记录
    @gen.coroutine
    def pushing(self, symbol):
        while True:
            gen.sleep(2)
            yield self.write_message(BDD_api.get_trades(symbol))

    @gen.coroutine
    def open(self, symbol):
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverWsKline(tornado.websocket.WebSocketHandler):
    # 币多多websocket的k线数据推送
    @gen.coroutine
    def pushing(self, symbol, interval):
        for i in BDD_websocket_client.get_kline(symbol, interval):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol, interval):
        gen.sleep(1)
        self.pushing(symbol, interval)


    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverWsTicker(tornado.websocket.WebSocketHandler):
    # 币多多websocket的前24小时交易对行情
    @gen.coroutine
    def pushing(self, symbol):
        for i in BDD_websocket_client.get_ticker(symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol):
        gen.sleep(1)
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverWsTrade(tornado.websocket.WebSocketHandler):
    # 币多多websocket的实时成交信息symbol=btcusdt
    @gen.coroutine
    def pushing(self, symbol):
        for i in BDD_websocket_client.get_trade(symbol):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol):
        gen.sleep(1)
        self.pushing(symbol)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class BDDserverWsDepth(tornado.websocket.WebSocketHandler):
    # 币多多websocket的深度盘口
    @gen.coroutine
    def pushing(self, symbol, step):
        for i in BDD_websocket_client.get_depth(symbol, step):
            yield self.write_message(i)

    @gen.coroutine
    def open(self, symbol, step):
        gen.sleep(1)
        self.pushing(symbol, step)

    def on_message(self, message):
        pass

    def check_origin(self, origin: str) -> bool:
        return True


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            # api
            url(r'/bix/api/alltickerData/bddex', BDDserverApiAllticker),
            url(r'/bix/api/klineData/bddex/(\w+)/(\d+)', BDDserverApiKline),
            url(r'/bix/api/DeptData/bddex/(\w+)/(step\d)', BDDserverApiDept),
            url(r'/bix/api/TradesData/bddex/(\w+)', BDDserverApiTrades),
            # ws
            url(r'/bix/ws/KlineData/bddex/(\w+)/(\d+\w+)', BDDserverWsKline),
            url(r'/bix/ws/TickerData/bddex/(\w+)', BDDserverWsTicker),
            url(r'/bix/ws/TradeData/bddex/(\w+)', BDDserverWsTrade),
            url(r'/bix/ws/DepthData/bddex/(\w+)/(\w+\d)', BDDserverWsDepth),

        ]
        tornado.web.Application.__init__(self, handlers)


if __name__ == "__main__":
    app = Application()
    server = HTTPServer(app)
    server.listen(port=8080)
    tornado.ioloop.IOLoop.current().start()
