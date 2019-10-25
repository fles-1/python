
import redis
pool=redis.ConnectionPool(host='192.168.100.30',
                          port=6379,db=0,
                          password='123456')
r=redis.StrictRedis(connection_pool=pool)
p=r.pubsub()
p.subscribe("spub","cctv1")
for item in p.listen():
    print("Listen on channel : %s "%item['channel'].decode())
    if item['type']=='message':
        data=item['data'].decode()
        print("From %s get message : %s"%(item['channel'].decode(),item['data'].decode()))
        if item['data']=='over':
            print(item['channel'].decode(),'停止发布')
            break
p.unsubscribe('spub')
print("取消订阅")

