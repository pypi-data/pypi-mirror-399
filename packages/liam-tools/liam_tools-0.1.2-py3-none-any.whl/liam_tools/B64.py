import base64
from liam_tools import pl

def enc(text: str) -> str:
    """
    将字符串编码为 Base64 格式字符串
    """
    if not text:
        return text
    # 编码为 bytes -> base64 编码 -> 转换回字符串
    text_bytes = text.encode('utf-8')
    encoded_bytes = base64.b64encode(text_bytes)
    return encoded_bytes.decode('utf-8')

def dec(encoded_text: str) -> str:
    """
    将 Base64 格式字符串解码为原字符串
    """
    if not encoded_text:
        return encoded_text
    try:
        # 转换为 bytes -> base64 解码 -> utf-8 解码为字符串
        decoded_bytes = base64.b64decode(encoded_text)
        return decoded_bytes.decode('utf-8')
    except (base64.binascii.Error, UnicodeDecodeError) as e:
        # 如果解码失败，返回原样或记录日志
        pl.e(f"Base64 解码失败: {e}")
        return encoded_text

if __name__ == '__main__':
    # 测试
    test_str = 'hello world'
    
    s1 = enc(test_str)
    pl.i(f"编码后: {s1}")  # 输出: aGVsbG8gd29ybGQ=
    
    result = dec(s1)
    pl.i(f"解码后: {result}")