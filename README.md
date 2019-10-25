# python
1.pip install uwsgi
2.创建flask服务api.py（debug,ip,port）
3建立ini文件在api.py同目录下
[uwsgi]
#plugin=python
http=0.0.0.0:5000
wsgi-file=/file/api.py
callable=server
touch-reload=/file/
4启动
uwsgi --ini /file/uwsgi.ini
