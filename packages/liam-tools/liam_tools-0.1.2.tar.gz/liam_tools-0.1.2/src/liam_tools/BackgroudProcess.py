from platform import system
from sys import stderr
from ctypes import windll

def hideConsole():
    """
    如果是 Windows 系统，则隐藏当前控制台窗口实现后台运行
    """

    if not 'Windows'==system():
        return

    try:

        # 获取当前控制台窗口句柄
        whnd = windll.kernel32.GetConsoleWindow()
        if whnd:
            # SW_HIDE = 0: 隐藏窗口并激活另一个窗口
            windll.user32.ShowWindow(whnd, 0)
            
            # 注意：不需要对 GetConsoleWindow 返回的句柄调用 CloseHandle
            # 因为该句柄是由系统管理的伪句柄或共享句柄。
    except Exception as e:
        # 防止因环境问题导致程序启动失败
        print(f"Failed to hide console: {e}", file=stderr)

# 执行隐藏操作
hideConsole()