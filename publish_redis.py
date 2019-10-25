
import redis
pool=redis.ConnectionPool(host='192.168.100.30',
                          port=6379,db=0,
                          password='123456')
r=redis.StrictRedis(connection_pool=pool)
while True:
    msg=input("publish: >>")
    if msg=="over":
        print("停止发布")
        break
    r.publish('spub',msg)

