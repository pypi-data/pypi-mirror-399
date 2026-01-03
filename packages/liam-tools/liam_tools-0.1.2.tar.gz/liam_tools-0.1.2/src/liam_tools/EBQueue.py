from threading import Condition
from liam_tools import pl, ustr

class EBQueue:
    """
    线程安全的队列类 (EBQueue)
    支持最大长度限制及阻塞获取
    """

    def __init__(self, maxSize=100):
        self.items = []
        self.maxSize = max(0, maxSize)
        # Condition 内部已经维护了一个 Lock，直接使用 Condition 即可
        self.condition = Condition()

    def put(self, item):
        """添加元素，如果队列满则移除最旧的元素"""
        if item is None:
            return
            
        with self.condition:
            if self.isFull():
                self._popLeft()
            self.items.append(item)
            self.condition.notify()

    def pull(self):
        """弹出一个元素（非阻塞）"""
        with self.condition:
            return self._popLeft()

    def get(self, timeout=None):
        """获取第一个元素（支持阻塞等待）"""
        with self.condition:
            # 如果队列为空，则进入等待
            if self.isEmpty():
                if not self.condition.wait(timeout):
                    return None  # 超时返回
            return self.items[0] if self.items else None

    def remove(self, item=None):
        """
        移除指定元素或第一个元素
        :param item: 如果为 None，则移除并返回第一个元素
        """
        with self.condition:
            if self.isEmpty():
                return None
            
            # 如果未指定 item，弹出第一个
            if item is None:
                return self._popLeft()
            
            # 如果指定了 item，尝试移除
            if item in self.items:
                self.items.remove(item)
                return item
            return None

    def isFull(self):
        """判断队列是否已满"""
        return 0 < self.maxSize <= len(self.items)

    def isEmpty(self):
        """判断队列是否为空"""
        return len(self.items) == 0

    def getCount(self):
        """获取当前队列长度"""
        with self.condition:
            return len(self.items)

    def printQueue(self):
        """打印队列内容"""
        with self.condition:
            if self.isEmpty():
                pl.i('The queue is empty')
            else:
                pl.i(self.items)

    def _popLeft(self):
        """内部私有方法：弹出第一个元素（不加锁，由调用者加锁）"""
        return self.items.pop(0) if self.items else None


def test():
    # 测试最大容量为 2 的队列
    msgs = EBQueue(2)

    pl.i("--- 插入两个元素 ---")
    for _ in range(2):
        val = ustr.getRandom(4)
        pl.i(f"Put: {val}")
        msgs.put(val)
    msgs.printQueue()

    pl.i("\n--- 插入第三个元素 (触发自动移除旧元素) ---")
    val = ustr.getRandom(4)
    pl.i(f"Put: {val}")
    msgs.put(val)
    msgs.printQueue()

    pl.i("\n--- 测试移除不存在的元素 ---")
    msgs.remove("non_existent")
    msgs.printQueue()

if __name__ == '__main__':
    test()