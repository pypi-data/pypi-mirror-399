from hashlib import md5, sha1
from os import path as ospath

class HashUtils:

    """
    提供字符串与文件的哈希计算工具类
    """

    @staticmethod
    def getMd5(content: str) -> str:
        """
        计算字符串的 MD5 值
        """
        if not content:
            return ""
        return md5(content.encode('utf-8')).hexdigest()

    @staticmethod
    def getSha1(content: str) -> str:
        """
        计算字符串的 SHA1 值
        """
        if not content:
            return ""
        return sha1(content.encode('utf-8')).hexdigest()

    @staticmethod
    def getFileMd5(filePath: str) -> str:
        """
        高效计算大文件的 MD5 值（分块读取）
        """
        if not ospath.isfile(filePath):
            return ""

        md5Obj = md5()
        try:
            with open(filePath, 'rb') as f:
                # 使用生成器迭代读取，代码更简洁
                for chunk in iter(lambda: f.read(4096), b""):
                    md5Obj.update(chunk)
            return md5Obj.hexdigest()
        except Exception as e:
            print(f"Error calculating MD5: {e}")
            return ""

# 使用示例
if __name__ == "__main__":

    testStr = "hello world"
    print(f"String MD5: {HashUtils.getMd5(testStr)}")
    print(f"String SHA1: {HashUtils.getSha1(testStr)}")