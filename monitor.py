import subprocess
import time
import paramiko
import select
import redis
import socket
import pymysql

from config import *

now_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
print(now_time)

now_day = time.strftime("%Y-%m-%d",time.localtime(time.time()))
print(now_day)


#  获取句柄数
def get_handle_total():
    cmd = 'cat /proc/sys/fs/file-nr'
    stdin, stdout, stderr = client.exec_command(cmd)
    # enumerate这个写法可遍历迭代对象以及对应索引
    for i, line in enumerate(stdout):
        result = line.strip("\n")
        result = result.split('\t')[0]
        print(result)
        print(type(result))
    return result



# 获取内存使用量
def get_mem_used():
    command = r"cat /proc/meminfo"
    stdin, stdout, stderr = client.exec_command(command)
    outs = stdout.readlines()
    res = {'total':0, 'free':0, 'buffers':0, 'cached':0}
    index = 0
    for line in outs:
        if (index == 4):
            break
        line = line.lstrip()
        memItem = line.lower().split()
        if memItem[0] == 'memtotal:':
            res['total'] = int(memItem[1])
            index = index + 1
            continue
        elif memItem[0] == 'memfree:':
            res['memfree'] = int(memItem[1])
            index = index + 1
            continue
        elif memItem[0] == 'buffers:':
            res['buffers'] = int(memItem[1])
            index = index + 1
            continue
        elif memItem[0] == 'cached:':
            res['cached'] = int(memItem[1])
            index = index + 1
            continue
    spu_used = res['total'] - res['free'] - res['buffers'] - res['cached']
    result = spu_used/res['total']
    spu_used = '%.2f%%'%(result*100)
    print(spu_used)
    return spu_used


def get_cpu():
    command = r"cat /proc/stat"
    stdin, stdout, stderr = client.exec_command(command)
    outs = stdout.readlines()
    for line in outs:
        line = line.lstrip()
        counters = line.split()
        if len(counters) < 5:
            continue
        if counters[0].startswith('cpu'):
            break
    total = 0
    for i in range(1, len(counters)):
        total = total + int(counters[i])
    idle = int(counters[4])
    return {'total':total, 'idle':idle}

# 获取cpu使用率
def get_cpu_used():
    counters1 = get_cpu()
    time.sleep(1)
    counters2 = get_cpu()
    idle = counters2['idle'] - counters1['idle']
    total = counters2['total'] - counters1['total']
    cpu_used = 100 - (idle * 100 / total)
    cpu_used = '%.2f%%'%(cpu_used)
    print(cpu_used)
    return cpu_used

# I/O操作
def get_IO_dis(dev):
    command = r"cat /proc/net/dev"
    stdin, stdout, stderr = client.exec_command(command)
    outs = stdout.readlines()
    res = {'total': 0, 'in': 0, 'out': 0}
    for line in outs:
        if line.lstrip().startswith(dev):
            line = line.replace(':', ' ')
            items = line.split()
            print('lenth',items)
            print(len(items))
            res['in'] = int(items[1])
            res['out'] = int(items[len(items) // 2 + 1])
            print(res["out"])
            res['total'] = res['in'] + res['out']
    if res['in'] > res['out']:
        return 'I'
    else:
        return 'O'

# 查看系统平均负载(特定时间间隔内，排队等待cpu处理得进程数，排队越多，cpu处理得越慢，平均负载就越大，aver_load < 3：系统性能良好，< 4：可以接受，>5:系统性能问题严重）
def aver_load():
    cmd = 'uptime'
    stdin, stdout, stderr = client.exec_command(cmd)
    # enumerate这个写法可遍历迭代对象以及对应索引
    for i, line in enumerate(stdout):
        result = line.strip("\n")
        sys_aver_load = result.split(':')[-1]
        print(sys_aver_load)
        return sys_aver_load

# 查看进程数量(获取进程绝对路径可以用pid来表示/proc/pid/exe   将pid更换即可
def get_process_info():
    command = 'ps aux'
    stdin,stdout,stderr = client.exec_command(command)
    index = 0
    for i, line in enumerate(stdout):
        result = line.strip("\n")
        result = result.split('\t')[0]
        result1 = result.split(' ')
        for i in range(result1.count('')):
            result1.remove('')
        # print(result1)
        if index == 0 :
            index += 1

            continue
        user = result1[0]
        pid = result1[1]
        cpu = float(result1[2])
        mem = float(result1[3])
        if cpu == 0.0 and mem == 0.0:
            continue
        print('user',user)
        print("pid",pid)
        print("cpu_used",cpu)
        print('mem',mem)

        index += 1





if __name__ == '__main__':
    cpu_list = []
    mem_list = []
    handle_list = []
    IO_list = []
    sys_list = []
    while True:
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        for dict in SEVER_LIST:
            host = dict['host']
            user = dict['user']
            pwd = dict['pwd']
            print('------------开始连接服务器(%s)-----------' % host)
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            print('------------开始认证......-----------')
            try:
                result = client.connect(host, 22, username=user, password=pwd, timeout=4)
                print(result)
                # 服务器开启
                status = 1
                print('------------认证成功!.....-----------')
            except Exception as e:
                # 服务器禁用或者账号密码错误
                print('------------认证失败!.....-----------')
                status = 0
                print(e)
                continue

            # 获取句柄数
            handle_total = get_handle_total()

            # 获取内存使用量
            mem_used = get_mem_used()

            # 获取cpu使用率
            cpu_used = get_cpu_used()

            # 判断是I还是O
            IO_dis = get_IO_dis('eth0')

            # 获取系统平均负载
            sys_load = aver_load()
            # 查看进程信息
            get_process_info()
            client.close()
##SERVER_LIST = [{'host':'','user':'','pwd':''},{'host':'','user':'','pwd':''}]
##
##
