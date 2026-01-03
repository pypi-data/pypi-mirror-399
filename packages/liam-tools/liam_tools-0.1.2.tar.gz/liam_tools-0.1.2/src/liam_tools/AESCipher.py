from binascii import hexlify, unhexlify
from hashlib import sha256
from Crypto.Cipher import AES
# from Crypto.Random import get_random_bytes


class AESCipher:
    """
    AES OCB 加解密工具类
    """

    def __init__(self, key: str):
        # AES key 必须是 16 / 24 / 32 字节
        self.key = sha256(key.encode("utf-8")).digest()

    def encrypt(self, plaintext: str) -> str:
        """
        加密，返回 hex 字符串（nonce + tag + ciphertext）
        """
        if not plaintext:
            return ""

        data = plaintext.encode("utf-8")

        cipher = AES.new(self.key, AES.MODE_OCB)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        # 拼接 nonce + tag + ciphertext
        encrypted = cipher.nonce + tag + ciphertext
        return hexlify(encrypted).decode("utf-8")

    def decrypt(self, encrypted_hex: str) -> str:
        """
        解密 hex 字符串
        """
        if not encrypted_hex:
            return ""

        raw = unhexlify(encrypted_hex)

        nonce = raw[:15]
        tag = raw[15:31]
        ciphertext = raw[31:]

        cipher = AES.new(self.key, AES.MODE_OCB, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        return plaintext.decode("utf-8")
