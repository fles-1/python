# coding: utf-8
# python模拟linux的守护进程

import sys, os, time, atexit, string
from signal import SIGTERM

__metaclass__ = type


class Daemon:
    def __init__(self, pidfile="/tmp/Daemon.pid", stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        # 需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.applicationName = "Application"
        self._homeDir = "/"
        # 调试模式是否开启
        self._verbose = False
        # 用户掩码，默认为0
        self._umask = 0

    # 获取守护进程掩码
    @property
    def umask(self):
        return self._umask

    # 设置守护进程掩码
    @umask.setter
    def umask(self, umask):
        self._umask = umask

    # 获取当前是否是调试模式
    @property
    def VerboseMode(self):
        return self._verbose

    # 调试模式开关，默认不是调试模式
    @VerboseMode.setter
    def VerboseMode(self, verboseMode):
        self._verbose = verboseMode

    # 调试模式和非调试模式设置
    def _verbosSwitch(self):
        # 调试模式是输出日志到指定文件，这些文件在对象初始化时指定
        if self._verbose:
            pass
            # self.stdin = '/dev/stdin'
            # self.stdout = '/dev/stdout'
            # self.stderr = '/dev/stderr'
        else:
            self.stdin = '/dev/null'
            self.stdout = '/dev/null'
            self.stderr = '/dev/null'

    def setApplicationName(self, appName):
        self.applicationName = appName

    # 获取和设置进程住目录
    @property
    def HomeDir(self):
        return self._homeDir

    @HomeDir.setter
    def HomeDir(self, homeDir):
        self._homeDir = homeDir

    # 这个方法的主要目的就是脱离主体，为进程创造环境
    def _daemonize(self):
        # 第一步
        try:
            # 第一次fork，生成子进程，脱离父进程，它会返回两次，PID如果等于0说明是在子进程里面，如果大于0说明当前是在父进程里
            pid = os.fork()
            # 如果PID大于0，说明当前在父进程里，然后sys.exit(0)，则是退出父进程，此时子进程还在运行。
            if pid > 0:
                # 退出父进程，此时linux系统的init将会接管子进程
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # 第二、三、四步
        os.chdir("/")  # 修改进程工作目录
        os.setsid()  # 设置新的会话，子进程会成为新会话的首进程，同时也产生一个新的进程组，该进程组ID与会话ID相同
        os.umask(self._umask)  # 重新设置文件创建权限，也就是工作目录的umask

        # 第五步
        try:
            # 第二次fork，禁止进程打开终端，相当于是子进程有派生一个子进程
            pid = os.fork()
            if pid > 0:
                # 子进程退出，孙子进程运行，此时孙子进程由init进程接管，在CentOS 7中是Systemed。
                sys.exit(0)
        except OSError as e:
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
            sys.exit(1)

        # 第六步
        # 把之前的刷到硬盘上
        sys.stdout.flush()
        sys.stderr.flush()
        # 重定向标准文件描述符
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'a+')
        # os.dup2可以原子化的打开和复制描述符，功能是复制文件描述符fd到fd2, 如果有需要首先关闭fd2. 在unix，Windows中有效。
        # File的 fileno() 方法返回一个整型的文件描述符(file descriptor FD 整型)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # 注册退出函数，根据文件pid判断是否存在进程
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile, 'w+').write('%s\n' % pid)

    # 程序退出后移除PID文件
    def delpid(self):
        os.remove(self.pidfile)

    def start(self, *args, **kwargs):
        # 检查pid文件是否存在以探测是否存在进程
        try:
            pid = self._getPid()
        except IOError:
            pid = None

        # 如果PID存在，则说明进程没有关闭。
        if pid:
            message = 'pidfile %s already exist. Process already running!\n'
            sys.stderr.write(message % self.pidfile)
            # 程序退出
            sys.exit(1)

        # 构造进程环境
        self._daemonize()
        # 执行具体任务
        self._run(*args, **kwargs)

    def stop(self):
        # 从pid文件中获取pid
        try:
            pid = self._getPid()
        except IOError:
            pid = None

        # 如果程序没有启动就直接返回不在执行
        if not pid:
            message = 'pidfile %s does not exist. Process not running!\n'
            sys.stderr.write(message % self.pidfile)
            return

        # 杀进程
        try:
            while 1:
                # 发送信号，杀死进程
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
                message = 'Process is stopped.\n'
                sys.stderr.write(message)
        except OSError as err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(err))
                sys.exit(1)

    # 获取PID
    def _getPid(self):
        try:
            # 读取保存PID的文件
            pf = open(self.pidfile, 'r')
            # 转换成整数
            pid = int(pf.read().strip())
            # 关闭文件
            pf.close()
        except IOError:
            pid = None
        except SystemExit:
            pid = None
        return pid

    # 重启的功能就是杀死之前的进程，然后再运行一个
    def restart(self, *args, **kwargs):
        self.stop()
        self.start(*args, **kwargs)

    # 获取守护程序运行状态
    def status(self):
        try:
            pid = self._getPid()
        except IOError:
            pid = None

        if not pid:
            message = "No such a process running.\n"
            sys.stderr.write(message)
        else:
            message = "The process is running, PID is %s .\n"
            sys.stderr.write(message % str(pid))

    def _run(self, *args, **kwargs):
        """
        这里是孙子进程需要做的事情，你可以继承这个类，然后重写这里的代码，上面其他的都可以不做修改
        """
        while True:
            """
            print 等于调用 sys.stdout.write(), sys.stdout.flush()是立即刷新输出。正常情况下如果是输出到控制台那么会立即输出
            但是重定向到一个文件就不会了，因为等于写文件，所以需要进行刷新进行立即输出。 下面使用print 还是 write都是一样的。
            """
            # print '%s:hello world\n' % (time.ctime(),)
            sys.stdout.write('%s:hello world\n' % (time.ctime(),))
            sys.stdout.flush()
            time.sleep(2)


if __name__ == '__main__':
    daemon = Daemon('/tmp/watch_process.pid', stdout='/tmp/watch_stdout.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.setApplicationName(sys.argv[0])
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print('unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print('usage: %s start|stop|restart|status' % sys.argv[0])
        sys.exit(2)
