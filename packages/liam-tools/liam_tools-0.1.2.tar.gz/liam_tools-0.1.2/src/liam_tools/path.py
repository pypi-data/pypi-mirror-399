from os import path as ospath
from os import getcwd, environ, makedirs, remove, rename, listdir, stat
from platform import system
import shutil
import time

# 将当前路径追加到系统路径 (建议使用绝对路径以避免环境干扰)
# syspath.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 基础配置
ROOT_DIR = 'fjlpy'

# --- 路径判断与基础操作 ---

def exist(path):
    return ospath.exists(path)

def isFile(path):
    return ospath.isfile(path)

def isDir(path):
    return ospath.isdir(path)

def size(path):
    """返回文件大小（字节），如果文件不存在则返回0"""
    return ospath.getsize(path) if isFile(path) else 0

# --- 目录获取 ---

def curDir():
    return getcwd()

def parentDir():
    """获取当前工作目录的父目录"""
    return ospath.dirname(getcwd())

def appdataTemp():
    """获取临时文件夹路径"""

    if 'Linux'==system()():
        return ospath.join(curDir(), 'data')
    # 使用 os.environ.get 提供默认值防止变量不存在时报错
    return environ.get('TEMP', ospath.join(curDir(), 'temp'))

# --- 文件/目录增删改 ---

def mkfolder(path):
    """递归创建文件夹"""
    if not exist(path):
        makedirs(path, exist_ok=True)

def rmFile(path):
    if path and isFile(path):
        remove(path)

def rmDir(path):
    if path and isDir(path):
        shutil.rmtree(path)

def renameFile(src, dst):
    """
    重命名文件
    0: 成功, -1: 目标已存在, 1: 失败/源文件不存在
    """
    if not isFile(src):
        return 1
    if exist(dst):
        return -1
    try:
        rename(src, dst)
        return 0
    except OSError:
        return 1

def rmFiles(directory, expired=172800):
    """清理过期文件 (默认2天)"""
    if not isDir(directory):
        return

    now = time.time()
    for name in listdir(directory):
        file_path = ospath.join(directory, name)
        if isFile(file_path):
            # 使用 st_mtime (修改时间) 通常比 st_atime (访问时间) 更准确
            if (now - stat(file_path).st_mtime) >= expired:
                remove(file_path)

# --- 时间相关 ---

def _getFileTime(fileName, time_type='mtime', timeStamp=False):
    """内部通用函数获取时间"""
    if not exist(fileName):
        return None
    stat_info = stat(fileName)
    ts = stat_info.st_mtime if time_type == 'mtime' else stat_info.st_ctime
    return ts if timeStamp else time.ctime(ts)

def cTime(fileName, timeStamp=False):
    return _getFileTime(fileName, 'ctime', timeStamp)

def mTime(fileName, timeStamp=False):
    return _getFileTime(fileName, 'mtime', timeStamp)

# --- 缓存管理 ---

def cache(category, filename):
    """通用的缓存路径生成"""
    folder = ospath.join(appdataTemp(), ROOT_DIR, category)
    mkfolder(folder)
    return ospath.join(folder, filename)

def cacheImg(fn):    return cache('Image', fn)
def cacheAudio(fn):  return cache('Audio', fn)
def cacheVideo(fn):  return cache('Video', fn)
def cacheDoc(fn):    return cache('Doc', fn)
def cacheOther(fn):  return cache('Other', fn)

# --- 路径处理工具 ---

def join(path, *paths):
    return ospath.join(path, *paths)

def split(path):
    return ospath.split(path)

def splitext(path):
    return ospath.splitext(path)

def filterName(path):
    """从路径中提取不含后缀的文件名"""
    return ospath.splitext(ospath.basename(path))[0]

# --- 读写操作 ---

def write(path, data, encoding='utf-8'):
    """写入文件，自动创建不存在的父目录"""
    mkfolder(ospath.dirname(path))
    with open(path, 'w', encoding=encoding) as f:
        f.write(data)

def read(path, encoding='utf-8'):
    if isFile(path):
        with open(path, 'r', encoding=encoding) as f:
            return f.read()
    return None

def listFiles(directory=None):
    directory = directory or curDir()
    return [ospath.join(directory, f) for f in listdir(directory)]

# --- Linux 专有路径 (遵循 XDG 标准) ---

def linuxExpandUser():
    return ospath.expanduser("~")

def linuxConfigDir():
    return environ.get("XDG_CONFIG_HOME", ospath.join(linuxExpandUser(), ".config"))

def linuxDataDir():
    return environ.get("XDG_DATA_HOME", ospath.join(linuxExpandUser(), ".local", "share"))
    
def linuxCacheDir():
    return environ.get("XDG_CACHE_HOME", ospath.join(linuxExpandUser(), ".cache"))