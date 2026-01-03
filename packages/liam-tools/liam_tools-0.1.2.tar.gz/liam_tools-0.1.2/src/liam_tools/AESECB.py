from Crypto.Cipher.AES import new, block_size, MODE_ECB
from Crypto.Util.Padding import pad, unpad
from base64 import b64encode, b64decode

class AESECB:

    def __init__(self, key=None):

        self.block_size = block_size
        self.mode = MODE_ECB
        self._key = None
        if key:
            self.key = self.formatKey(key)

    def formatKey(self, key):

        """确保 key 长度为 16, 24 或 32 字节"""
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        length = len(key)
        if length <= 16:
            return key.ljust(16, b'0')
        elif length <= 24:
            return key.ljust(24, b'0')
        elif length <= 32:
            return key.ljust(32, b'0')
        else:
            return key[:32]

    def getCipher(self, key):

        """获取 cipher 实例"""
        target_key = self.formatKey(key) if key else self.key
        if not target_key:
            raise ValueError("Key must be provided")
        return new(target_key, self.mode)

    def encryptBase64(self, text, key=None):

        """加密并返回 Base64 字符串"""
        if not text: return ""
        cipher = self.getCipher(key)
        # 统一使用 PKCS7 填充
        raw = pad(text.encode('utf-8'), self.block_size)
        ciphertext = cipher.encrypt(raw)
        return b64encode(ciphertext).decode('utf-8')

    def decryptBase64(self, encoded_text, key=None):

        """解密 Base64 字符串"""
        if not encoded_text: return ""
        cipher = self.getCipher(key)
        ciphertext = b64decode(encoded_text)
        data = cipher.decrypt(ciphertext)
        return unpad(data, self.block_size).decode('utf-8')

    def encryptHex(self, text, key=None):

        """加密并返回大写 Hex 字符串"""
        if not text: return ""
        cipher = self.getCipher(key)
        raw = pad(text.encode('utf-8'), self.block_size)
        ciphertext = cipher.encrypt(raw)
        return ciphertext.hex().upper()

    def decryptHex(self, hex_text, key=None):

        """解密 Hex 字符串"""
        if not hex_text: return ""
        cipher = self.getCipher(key)
        ciphertext = bytes.fromhex(hex_text)
        data = cipher.decrypt(ciphertext)
        return unpad(data, self.block_size).decode('utf-8')

# --- 测试代码 ---
if __name__ == '__main__':

    KEY = 'key' # 'a7e47aa84c5f2e10'
    tester = AESECB(KEY)
    
    test_msg = "hello kotlin"
    
    # Base64 测试
    b64_str = tester.encryptBase64(test_msg)
    print(f"Base64 Enc: {b64_str}")
    print(f"Base64 Dec: {tester.decryptBase64(b64_str)}")
    
    # Hex 测试
    hex_str = tester.encryptHex(test_msg)
    print(f"Hex Enc: {hex_str}")
    print(f"Hex Dec: {tester.decryptHex(hex_str)}")