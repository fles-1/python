# -- coding: utf-8 --
import requests
from redis import StrictRedis
import json
import time


class SpiderPushRedis:
    redis_con = StrictRedis(host='127.0.0.1', password=123456, port=6379, db=0)
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"
    # 代理隧道验证信息
    proxyUser = "HQ40Y9GN5DXUL40D"
    proxyPass = "264D80183B0FBB52"
    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {"host": proxyHost, "port": proxyPort, "user": proxyUser,
                                                                "pass": proxyPass, }

    proxies = {"http": proxyMeta, "https": proxyMeta, }
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"}
    s1 = []
    s2 = []
    s3 = []
    s4 = []
    s5 = []
    s6 = []
    s7 = []
    s8 = []
    s9 = []
    s10 = []
    s11 = []
    s12 = []
    s13 = []
    s14 = []
    s15 = []
    s16 = []
    s17 = []
    s18 = []
    s19 = []
    s20 = []

    def __init__(self, url):
        self.page_data = None
        self.json_dict = None
        self.muti_list = None
        self.url = url
        self.json_data = {"filter": [{"left": "CCI20", "operation": "nempty"}],
                          "options": {"active_symbols_only": True, "lang": "zh"},
                          "symbols": {"query": {"types": []}, "tickers": []},
                          "columns": ["name", "close", "change", "change_abs", "high", "low", "volume", "Recommend.All",
                                      "exchange", "Low.3M", "High.3M", "Perf.3M", "price_52_week_low",
                                      "price_52_week_high", "Low.6M", "High.6M", "Perf.6M", "MACD.macd", "CCI20",
                                      "description", "name", "subtype", "update_mode", "pricescale", "minmov",
                                      "fractional", "minmove2", "MACD.macd", "MACD.signal", "CCI20", "CCI20[1]"],
                          "sort": {"sortBy": "CCI20", "sortOrder": "desc"}, }

    def push_redis(self):
        while True:
            time.sleep(5)
            self.page_data = requests.post(self.url, json=self.json_data,
                                           headers=self.headers).text
            self.json_dict = json.loads(self.page_data)

            for i in range(self.json_dict['totalCount']):
                self.s1.append(self.json_dict['data'][i]['d'][0])
                self.s2.append(self.json_dict['data'][i]['d'][1])
                self.s3.append(self.json_dict['data'][i]['d'][2])
                self.s4.append(self.json_dict['data'][i]['d'][3])
                self.s5.append(self.json_dict['data'][i]['d'][4])
                self.s6.append(self.json_dict['data'][i]['d'][5])
                self.s7.append(self.json_dict['data'][i]['d'][6])
                self.s8.append(self.json_dict['data'][i]['d'][7])
                self.s9.append(self.json_dict['data'][i]['d'][8])
                self.s10.append(self.json_dict['data'][i]['d'][9])
                self.s11.append(self.json_dict['data'][i]['d'][10])
                self.s12.append(self.json_dict['data'][i]['d'][11])
                self.s13.append(self.json_dict['data'][i]['d'][12])
                self.s14.append(self.json_dict['data'][i]['d'][13])
                self.s15.append(self.json_dict['data'][i]['d'][14])
                self.s16.append(self.json_dict['data'][i]['d'][15])
                self.s17.append(self.json_dict['data'][i]['d'][16])
                self.s18.append(self.json_dict['data'][i]['d'][17])
                self.s19.append(self.json_dict['data'][i]['d'][18])
                t = time.time()
                self.s20.append(t)
            self.muti_list = zip(self.s1, self.s2, self.s3, self.s4, self.s5, self.s6, self.s7, self.s8, self.s9,
                                 self.s10, self.s11, self.s12, self.s13, self.s14, self.s15, self.s16, self.s17,
                                 self.s18, self.s19, self.s20)
            for i in self.muti_list:
                self.redis_con.publish('spub', str(i))  # 发布在spub频道

    def run(self):

        self.push_redis()


if __name__ == "__main__":

    spider_exam = SpiderPushRedis('https://scanner.tradingview.com/crypto/scan')
    spider_exam.run()
