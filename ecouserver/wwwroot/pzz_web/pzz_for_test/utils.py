import base64
import json
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

unpad = lambda s: s[:-ord(s[len(s) - 1:])]

class WXBizDataCrypt:
    def __init__(self, appId, sessionKey):
        self.appId = appId
        self.sessionKey = sessionKey

    def decrypt(self, encryptedData, iv):
        # base64 decode
        sessionKey = base64.b64decode(self.sessionKey)
        encryptedData = base64.b64decode(encryptedData)
        iv = base64.b64decode(iv)

        cipher = AES.new(sessionKey, AES.MODE_CBC, iv)

        decrypted = json.loads(self._unpad(cipher.decrypt(encryptedData)))

        if decrypted['watermark']['appid'] != self.appId:
            raise Exception('Invalid Buffer')

        return decrypted

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

def decrypt(data, key):
    key = key.encode('utf8')[0:16]
    data = base64.b64decode(data)
    cipher = AES.new(key, AES.MODE_ECB)
    text_decrypted = unpad(cipher.decrypt(data))
    text_decrypted = text_decrypted.decode('utf8')
    # print(text_decrypted)
    return text_decrypted
