# -- coding: utf-8 --
import requests
import json
class AOFEXAPI:
    # https://openapi.aofex.com/openApi/market/kline?&symbol=BTC-USDT&period=1min
    def __int__(self):
        pass

    def get_kline(self, kline, symbol, period):
        data = requests.get("https://openapi.aofex.com/openApi/market/%s?&symbol=%s&period=%s" % (kline, symbol, period
                                                                                                  )).text
        data_dict = json.loads(data)

        del data_dict['result']['data'][0]['id']
        data_dict['result']['data'][0]['volume'] = data_dict['result']['data'][0].pop('vol')
        data_dict['result']['data'][0]['timestamp'] = data_dict['result']['ts']

        data_data = {"data": {"data": data_dict['result']['data'][0]},
                     "interval": period, "symbol": data_dict['result']['symbol'].replace('-', '').lower(),
                     "rate": 100}
        return data_data


if __name__ == "__main__":
    aofexapi = AOFEXAPI()
    print(aofexapi.get_kline('kline', 'BTC-USDT', '1min'))
