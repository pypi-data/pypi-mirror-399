from colorama import init
from liam_tools import ustr

# 初始化 colorama
init(autoreset=True)

# --- 核心处理函数 ---

def _format_msg(arg, color_func=None):
    """内部通用格式化函数"""
    msg = '{}'.format(arg)
    return color_func(msg) if color_func else ustr.sdefault(msg)

def _out(msg, end='\n'):
    """统一输出口，确保 flush 始终开启"""
    print(msg, end=end, flush=True)

# --- 公共接口 ---

def i(arg):
    """普通信息输出 (Default)"""
    _out(_format_msg(arg))

def ituple(*args):
    """元组格式化普通输出"""
    _out(ustr.sdefault(ustr.format_string(args)))

def d(arg):
    """调试信息输出 (Green)"""
    _out(_format_msg(arg, ustr.sgreen))

def dtuple(*args):
    """元组格式化调试输出"""
    _out(ustr.sgreen(ustr.format_string(args)))

def w(arg):
    """警告信息输出 (Red)"""
    _out(_format_msg(arg, ustr.sred))

def wtuple(*args):
    """元组格式化警告输出"""
    _out(ustr.sred(ustr.format_string(args)))

def end(arg, color=None):
    """
    同一行打印
    :param color: 'red', 'green' 或 None
    """
    color_map = {
        'red': ustr.sred,
        'green': ustr.sgreen
    }
    # 使用映射表替代 if-elif 链
    target_func = color_map.get(color)
    _out(_format_msg(arg, target_func), end='')

# --- 对齐工具 (优化后支持颜色和宽度自定义) ---

def lalign(arg, width=20, color=None):
    """左对齐"""
    formatted = f'{arg:<{width}}'
    _out(_format_msg(formatted, color_func=_get_color_by_name(color)))

def calign(arg, width=20, color=None):
    """居中对齐"""
    formatted = f'{arg:^{width}}'
    _out(_format_msg(formatted, color_func=_get_color_by_name(color)))

def ralign(arg, width=20, color=None):
    """右对齐"""
    formatted = f'{arg:>{width}}'
    _out(_format_msg(formatted, color_func=_get_color_by_name(color)))

def _get_color_by_name(name):
    """辅助函数：根据名称获取 ustr 颜色函数"""
    return {
        'red': ustr.sred,
        'green': ustr.sgreen
    }.get(name)