from config import app
from flask import render_template, request, redirect, session
import requests
import json
from datetime import timedelta
from functools import wraps

USER = {'username': 'admin', 'password': "admin"}
# 数据库链接的配置，此项必须，格式为（数据库+驱动://用户名:密码@数据库主机地址:端口/数据库名称）
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost:3306/alchemy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # 跟踪对象的修改，在本例中用不到调高运行效
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 设置session的保存时间。
app.config['SECRET_KEY'] = '@#！￥%^'   # 加盐随意设置


# 用户会话装饰器装饰多个视图函数
def wrapper(func):
    @wraps(func)  # 保存原来函数的所有属性,包括文件名
    def inner(*args, **kwargs):
        # 校验session
        if session.get("user"):
            ret = func(*args, **kwargs)  # func = home
            return ret
        else:
            return redirect("/login")
    return inner

# 首页
@app.route('/index/')
@wrapper
def index():
    if session.get('user'):
        return render_template('index.html')
    else:
        return redirect("/login")

# 登录
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        if request.form.get("username") == USER["username"] and request.form.get("password") == USER["password"]:
            session["user"] = request.form.get("username")
            return redirect("/index")
        else:
            return redirect("/login")

# 用户
@app.route('/user/')
def user():
    tlist = sorted(ip_count.items(), key=lambda x: x[1], reverse=True)[:10]
    ip_area = []
    for i, v in tlist:
        area = get_area(i)
        ip_area.append(area)
    z = zip(tlist, ip_area)
    userlist = sorted(user_count.items(), key=lambda x: x[1], reverse=True)
    if session.get("user"):
        return render_template('user.html', z=z, userlist=userlist)
    else:
        return redirect("/login")

# 接口
@app.route('/interface/')
@wrapper
def interface():
    interface_list = sorted(interface_count.items(), key=lambda x: x[1], reverse=True)[:100]
    if session.get("user"):
        return render_template('interface.html', interface_list=interface_list)
    else:
        return redirect("/login")


ip_count = {}
user_count = {}
interface_count = {}

f = open(r'C:\Users\Administrator\Desktop\log\access.log', 'r')
# 字典排序
for line in f.readlines():
    ip = line.strip().split()[0]
    ip_count[ip] = ip_count[ip] + 1 if ip in ip_count else 1

    u = line[line.find('('):line.find(')')]
    if "iPhone" in u:
        u = 'iPhone'
        user_count[u] = user_count[u] + 1 if u in user_count else 1

    if "Android" in u:
        u = 'Android'
        user_count[u] = user_count[u] + 1 if u in user_count else 1

    interface = line[line.find('"'):line.find('(')]
    i = interface.split()
    s = i[1] + ' ' + i[3]
    interface_count[s] = interface_count[s] + 1 if s in interface_count else 1


# 获取ip所在区域
def get_area(ipip):
    url = 'http://freeapi.ipip.net/'+ipip
    data = requests.get(url).text
    return json.loads(data)


f.close()
if __name__ == "__main__":
    app.run("0.0.0.0")
