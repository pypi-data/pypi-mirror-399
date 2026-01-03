"""加密解密工具"""


def encryptWithAES_ECB(data: str, aesKey: str, noPadding: bool) -> str:
    """AES加密"""
    return ""


def decryptWithAES_ECB(data: str, aesKey: str, noPadding: bool) -> str:
    """AES解密"""
    return ""


def encryptWithRSA(data: str, publicKeyBase64: str) -> str:
    """RSA加密"""
    return ""


def decryptWithRSA(encryptedData: str, privateKeyBase64: str) -> str:
    """RSA解密"""
    return ""


def md5(source: str) -> str:
    """计算MD5"""
    return ""


def sha1(source: str, key: str = None) -> str:
    """计算SHA1"""
    return ""


def sha256(source: str, key: str = None) -> str:
    """计算SHA256"""
    return ""
