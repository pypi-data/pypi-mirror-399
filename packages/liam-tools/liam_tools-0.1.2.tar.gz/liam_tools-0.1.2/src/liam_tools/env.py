from os import environ

def getEnv(envName, defaultValue=None, castType=str):
    """
    获取并转换环境变量类型
    """
    value = environ.get(envName, defaultValue)
    if value is None:
        return defaultValue
    try:
        # 处理布尔值的特殊情况
        if castType == bool and isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return castType(value)
    except (ValueError, TypeError):
        return defaultValue