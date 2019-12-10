import time
import datetime
#获取当前时间戳
t=time.time()
local_time=time.localtime(t)#获取本地时间
now=time.strftime('%Y-%m-%d %H:%m:%S',local_time)#获取本地格式化的时间
#获取前第3天日期
d3=(datetime.datetime.now() + timedelta(days=-3)).strftime('%Y-%m-%d')
print(d3)
