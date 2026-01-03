import json

def s2Dict(jsonStr):
    """将 JSON 字符串转换为字典"""
    try:
        return json.loads(jsonStr)
    except (json.JSONDecodeError, TypeError):
        return None

def var2Dict(value):
    """
    安全地将字符串表现形式的字典转换为字典对象
    优化：使用 json.loads 或 ast.literal_eval 替代危险的 eval
    """
    import ast
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return None

def dict2Str(dataDict):
    """将字典转换为紧凑的 JSON 字符串"""
    if not verify(dataDict):
        return ""
    # separators 去除空格，节省空间
    return json.dumps(dataDict, separators=(',', ':'), ensure_ascii=False)

def get(dataDict, *keys):
    """
    深层获取字典值，支持多级 key
    示例：get(d, 'user', 'profile', 'name')
    """
    if not verify(dataDict) or not keys:
        return None

    value = dataDict
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def value(dataDict, key, default=None):
    """获取指定 key 的值，不存在则返回默认值"""
    if not verify(dataDict):
        return default
    return dataDict.get(key, default)

def hasKey(dataDict, key):
    """判断是否存在指定的 key"""
    if not verify(dataDict) or not key:
        return False
    return key in dataDict

def verify(dataDict):
    """校验对象是否为非空字典"""
    if not dataDict or not isinstance(dataDict, dict):
        return False
    return True

def formatDict(dataDict) -> str:
    """将字典格式化为 key:value 换行形式"""
    if not verify(dataDict): 
        return ""

    # 使用列表推导式和 join 提高字符串拼接性能
    return "\n".join([f"{k}:{v}" for k, v in dataDict.items()])

def prt(arg):
    """打印字典或普通参数"""
    if arg is None:
        print('Param is null')
        return

    if isinstance(arg, dict):
        # 优化打印格式，增加可读性
        print(formatDict(arg))
    else:
        print(str(arg))

# --- 扩展功能：合并字典 ---
def merge(dictA, dictB):
    """合并两个字典"""
    if not verify(dictA): return dictB
    if not verify(dictB): return dictA
    res = dictA.copy()
    res.update(dictB)
    return res