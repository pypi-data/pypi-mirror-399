import os, re, string, random, inspect, operator
from operator import contains
from re import findall
from unicodedata import east_asian_width

# 正则示例 https://www.51cto.com/article/637513.html
# 正则示例 https://blog.csdn.net/jlulxg/article/details/84650683

"""
文字颜色规则
https://www.cnblogs.com/easypython/p/9084426.html
\033[1;32;41m   #---1-高亮显示 32-前景色绿色  40-背景色红色---
"""

# 不显示颜色
# 导入 from colorama import init 然后设置 init(autoreset=True)

# reset color text
from colorama import init
init(autoreset=True)

def startswith():

	txt = 'abcde'
	beg = 0
	end = len(txt)
	return txt.startswith('a', beg, end)

def split():

	txt = 'abcd\nefg\nhij'
	txt.split('\n', 1) # 第二个参数表示处理几次

def tostring(param):
	return any2str(param)

def any2str(arg):
    return arg if isinstance(arg, str) else '{}'.format(arg)

# 格式化为string 会保留原类型 *args 表示任何多个无名参数，它本质是一个 tuple
def format_string(*args):
	return ''.join('%s' %(repr(item)) for item in args)

# 获取当前工作目录
def getcwd():
    return os.getcwd()

# 随机数
def getRandom(length):
    letters_digits = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return (''.join(random.choice(letters_digits) for i in range(length)))

# 带颜色的文字
def sred(value):
    # return '\033[0;31;40m{}'.format(value)
    return '\033[0;31m{}'.format(value)

def sblue(value):
    # return '\033[0;34;40m{}'.format(value)
    return '\033[0;34m{}'.format(value)

def sgreen(value):
    # return '\033[0;32;40m{}'.format(value)
    return '\033[0;32m{}'.format(value)

def sqing(value):
    return '\033[0;36m{}'.format(value)

def sdefault(value):
     return '\033[0m{}'.format(value)

# 文件名 arg:文件路径
def fileName(arg):
    # split 分割路径和文件名
    # splitext 分割文件名和扩展名
    return os.path.splitext(arg)[0]

# 文件后缀名(以.结尾的文件路径)
def fileSuffix(arg):
    return os.path.splitext(arg)[-1]

# 过滤出数字
def filterNumber(arg):
    return re.sub(u'([^\u0030-\u0039])', '', arg)

# 过滤出座机号码
def landLine(arg):
    return re.findall('^0\\d{2,3}\\d{7,8}$', filterNumber(arg))

def areaCode(arg):
    if arg.startswith('01') or arg.startswith('02'): # 取前3位
        return arg[:3]
    elif arg.startswith('03') or arg.startswith('04') or arg.startswith('05') or arg.startswith('06') or arg.startswith('07') or arg.startswith('08') or arg.startswith('09'): # 取前4位
        return arg[:4]

    return None

# 获取方法名
def funcName():
    return inspect.stack()[1][3]

# 是否包含子串 7种方法
def subIn(full, sub):
    return sub in full

def subFind(full, sub):
    return full.find(sub) != -1

def subIndex(full, sub):
    try:
        full.index(sub)
        return True
    except:
        return False

def subCount(full, sub):
    return full.count(sub) > 0

def subContains(full, sub):
    return full.__contains__(sub)

def subOperator(full, sub):
    return contains(full, sub)

def subRe(full, sub):
    return True if findall(sub, full) else False

def isChinese(ch):
     return '\u4e00' <= ch <= '\u9fff'

# 字符串宽度
def sWidth(value):
    
    width = 0
    for ch in value:
        width += chWidth(ch)

    return width

def fill(value, width):
    w = sWidth(value)
    if w >= width:
        return value

    space = ' '*(width-w)
    return f'{value}{space}'

# 字符宽度
def chWidth(ch):
    return 2 if east_asian_width(ch) in ('F', 'W', 'A') else 1

# 替换示例
def replace():

    s = 'hello python'
    s.replace('he', 'new')

# 将输入字符串划分为最大长度为 max 的子字符串列表
def splitString(inp, max=1024):

    substrings = []  
    for i in range(0, len(inp), max):  
        substrings.append(inp[i:i+max])
    return substrings

# 示例
    # 遍历并返回元祖
    # items = [(item, path.mTime(item)) for item in lts]

    # 排序 reverse是否倒序
    # sorted(items, key=lambda x: x[1], reverse=False)