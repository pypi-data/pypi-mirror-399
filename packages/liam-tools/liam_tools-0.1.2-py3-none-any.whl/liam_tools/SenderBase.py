from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.base import STATE_RUNNING
from time import strftime, localtime
from liam_tools import pl, udict, EBQueue  # 使用之前优化后的队列类

class ForceSender:
    """
    强制发送基类
    支持失败自动重试、阶梯式延迟等待
    """

    def __init__(self, scheduler=None):
        # 初始配置
        self.delayMultiple = 1  # 失败延迟倍数
        self.msgQueue = EBQueue(100)  #
        self.maxRetries = 3     # 单次最大尝试次数
        
        # 调度器初始化
        self.scheduler = scheduler or BackgroundScheduler(timezone='Asia/Taipei')
        
        if self.scheduler.state != STATE_RUNNING:
            self.scheduler.start()
            
        # 启动消息轮询任务
        self.scheduler.add_job(
            self.messageLooper, 
            trigger='date',  # 立即执行一次，内部维持循环
            misfire_grace_time=None,
            id=f"{self.getName()}_looper"
        )

    def onMessage(self, msg):
        """
        消息入口
        """
        try:
            if not udict.verify(msg):  #
                return
            self.msgQueue.put(msg)     #
        except Exception as exc:
            pl.wtuple('OnMessage Error', exc) #

    def messageLooper(self):
        """
        消息循环处理器
        """
        while True:
            try:
                # 1. 检查队列是否为空 (阻塞或休眠)
                if self.msgQueue.isEmpty(): #
                    sleep(1)
                    continue

                # 2. 获取但不立即移除 (Peek)
                msg = self.msgQueue.get() #
                if not msg:
                    continue

                success = self._executeSendWithRetry(msg)

                if success:
                    # 发送成功：从队列移除并重置延迟
                    self.msgQueue.remove(msg) #
                    self.delayMultiple = 1
                else:
                    # 发送彻底失败：计算阶梯延迟 (最长 1 天)
                    self._handleFailureWait()

            except Exception as exc:
                pl.w(f"MessageLooper Exception: {exc}") #
                sleep(5)

    def _executeSendWithRetry(self, msg):
        """
        内部逻辑：执行单条消息的发送与重试
        """
        retryCount = 0
        while retryCount < self.maxRetries:
            try:
                if self.send(msg):
                    pl.d(f"[{self.getName()}] Sent Successfully\n{format()}") #
                    udict.prt(msg) #
                    return True
            except Exception as e:
                pl.w(f"Send Exception: {e}") #

            retryCount += 1
            if retryCount < self.maxRetries:
                sleep(2) # 失败后的短促重试间隔

        pl.w(f"[{self.getName()}] Max retries reached ({self.maxRetries}). Task will wait.") #
        return False

    def _handleFailureWait(self):
        """
        处理失败后的等待逻辑 (阶梯式避让)
        """
        waitSecs = 10 * self.delayMultiple
        pl.w(f"Next retry will be after {waitSecs}s (Multiple: {self.delayMultiple})") #
        
        sleep(waitSecs)
        
        # 阶梯逻辑：上限约为 1 天 (86400秒 / 10 = 8640)
        if self.delayMultiple >= 8640:
            self.delayMultiple = 1
        else:
            self.delayMultiple += 1

    def send(self, msg):
        """
        子类需重写此方法实现具体发送逻辑
        """
        return True
    
    def getName(self):
        """获取类名"""
        return self.__class__.__name__
    
    def format() -> str:
        return strftime("%Y-%m-%d %H:%M:%S", localtime())

if __name__ == '__main__':
    # 示例用法
    # sender = ForceSender()
    pass