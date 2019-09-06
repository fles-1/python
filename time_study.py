import time
#获取当前时间戳
t=time.time()
local_time=time.localtime(t)#获取本地时间
now=time.strftime('%Y-%m-%d %H:%m:%S',local_time)#获取本地格式化的时间
