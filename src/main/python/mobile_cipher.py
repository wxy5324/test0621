"""
手机号加解密模块
--------------------
基于国密SM4算法，对手机号进行加密和解密操作。
实现与Java端BouncyCastle的SM4加密完全兼容，确保跨语言加解密一致性。
主要功能：
    - 单个/批量手机号加密与解密
    - SM4/ECB模式 + PKCS5填充
    - Base64编码输出
    - 支持生成客户数据并批量写入MySQL数据库
"""

import base64
import logging
import pymysql
from pymysql.err import OperationalError, ProgrammingError


# ==================== 日志配置 ====================
# 设置日志级别为INFO，便于追踪加解密过程及异常
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== SM4 国密算法常量 ====================
# 以下常量严格对齐BouncyCastle的SM4实现，确保与Java端加密结果一致

# SM4 S盒（Substitution Box）：256个字节的替换表，用于字节替换变换
# 每个输入字节通过查表得到输出，是SM4算法非线性变换的核心
SM4_SBOX = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c, 0x05,
    0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86, 0x06, 0x99,
    0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed, 0xcf, 0xac, 0x62,
    0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa, 0x75, 0x8f, 0x3f, 0xa6,
    0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c, 0x19, 0xe6, 0x85, 0x4f, 0xa8,
    0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb, 0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35,
    0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25, 0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87,
    0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52, 0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e,
    0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38, 0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1,
    0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34, 0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3,
    0x1d, 0xf6, 0xe2, 0x2e, 0x82, 0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f,
    0xd5, 0xdb, 0x37, 0x45, 0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51,
    0x8d, 0x1b, 0xaf, 0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8,
    0x0a, 0xc1, 0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0,
    0x89, 0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39, 0x48
]

# SM4 系统参数 FK（Family Key）：4个32位常量，用于密钥扩展的初值异或
SM4_FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

# SM4 固定参数 CK：32个32位常量，每轮密钥扩展时使用，保证轮密钥的随机性
SM4_CK = [
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
]


# ==================== SM4 底层运算函数 ====================
# 以下函数实现SM4算法的基本运算，位运算逻辑严格对齐Java实现

def sm4_rotl(x: int, n: int) -> int:
    """
    32位整数循环左移
    与Java的Integer.rotateLeft(x, n)行为一致，确保跨语言兼容
    :param x: 待移位整数（32位）
    :param n: 左移位数
    :return: 循环左移后的结果
    """
    return ((x << n) & 0xFFFFFFFF) | (x >> (32 - n))

def sm4_sub_byte(x: int) -> int:
    """
    字节替换：将32位整数按字节拆分为4个字节，每个字节通过S盒查表替换后重组
    严格对齐BouncyCastle的S盒实现
    :param x: 输入的32位整数
    :return: 替换后的32位整数
    """
    return (SM4_SBOX[(x >> 24) & 0xFF] << 24) | \
           (SM4_SBOX[(x >> 16) & 0xFF] << 16) | \
           (SM4_SBOX[(x >> 8) & 0xFF] << 8) | \
           SM4_SBOX[x & 0xFF]

def sm4_l(x: int) -> int:
    """
    线性变换L：用于加解密轮函数，通过多次循环左移后异或实现扩散
    对齐Java的SM4 L变换：L(B) = B ⊕ (B<<<2) ⊕ (B<<<10) ⊕ (B<<<18) ⊕ (B<<<24)
    :param x: 输入的32位整数
    :return: 变换后的32位整数
    """
    return x ^ sm4_rotl(x, 2) ^ sm4_rotl(x, 10) ^ sm4_rotl(x, 18) ^ sm4_rotl(x, 24)

def sm4_l_(x: int) -> int:
    """
    线性变换L'：用于密钥扩展，与L变换参数不同
    公式：L'(B) = B ⊕ (B<<<13) ⊕ (B<<<23)
    :param x: 输入的32位整数
    :return: 变换后的32位整数
    """
    return x ^ sm4_rotl(x, 13) ^ sm4_rotl(x, 23)

def sm4_key_expansion(key: bytes) -> list:
    """
    密钥扩展：将16字节主密钥扩展为32个轮密钥
    严格对齐BouncyCastle的SM4密钥扩展算法
    :param key: 16字节的SM4密钥
    :return: 32个32位轮密钥的列表 rk[0..31]
    """
    # 将16字节密钥按大端序转为4个32位整数 MK[0..3]
    mk = [
        int.from_bytes(key[0:4], byteorder='big'),
        int.from_bytes(key[4:8], byteorder='big'),
        int.from_bytes(key[8:12], byteorder='big'),
        int.from_bytes(key[12:16], byteorder='big')
    ]
    
    # 初始密钥：K[0..3] = MK[0..3] ⊕ FK[0..3]
    k = [mk[i] ^ SM4_FK[i] for i in range(4)]
    rk = []  # 轮密钥列表
    
    # 32轮迭代生成32个轮密钥
    for i in range(32):
        t = k[1] ^ k[2] ^ k[3] ^ SM4_CK[i]  # 异或合并
        t = sm4_sub_byte(t)                  # 字节替换
        t = sm4_l_(t)                         # 线性变换
        k[0] = k[0] ^ t                       # 更新K[0]
        # 循环左移：K整体左移一位，原K[0]移至末尾
        k[0], k[1], k[2], k[3] = k[1], k[2], k[3], k[0]
        rk.append(k[3])  # 当前轮密钥为移位后的K[3]
    
    return rk

def sm4_encrypt_block(key: bytes, data: bytes) -> bytes:
    """
    加密单个16字节数据块，采用ECB模式（无链接）
    与Java的SM4/ECB模式完全一致
    :param key: 16字节SM4密钥
    :param data: 待加密的16字节数据块
    :return: 加密后的16字节密文
    """
    rk = sm4_key_expansion(key)
    
    # 将16字节明文按大端序拆分为4个32位整数 X[0..3]
    x = [
        int.from_bytes(data[0:4], byteorder='big'),
        int.from_bytes(data[4:8], byteorder='big'),
        int.from_bytes(data[8:12], byteorder='big'),
        int.from_bytes(data[12:16], byteorder='big')
    ]
    
    # 32轮Feistel结构加密，每轮使用一个轮密钥
    for i in range(32):
        t = x[1] ^ x[2] ^ x[3] ^ rk[i]   # 异或轮密钥
        t = sm4_sub_byte(t)               # S盒替换
        t = sm4_l(t)                      # 线性变换
        x[0], x[1], x[2], x[3] = x[1], x[2], x[3], x[0] ^ t  # 更新并循环移位
    
    # 反序输出：解密时需反向，此处为加密后的最终排列
    return (
        x[3].to_bytes(4, byteorder='big') +
        x[2].to_bytes(4, byteorder='big') +
        x[1].to_bytes(4, byteorder='big') +
        x[0].to_bytes(4, byteorder='big')
    )

def sm4_decrypt_block(key: bytes, data: bytes) -> bytes:
    """
    解密单个16字节密文块，ECB模式
    与加密过程对称，轮密钥逆序使用（rk[31]..rk[0]）
    :param key: 16字节SM4密钥
    :param data: 待解密的16字节密文块
    :return: 解密后的16字节明文
    """
    rk = sm4_key_expansion(key)
    
    # 将16字节密文按大端序拆分为4个32位整数
    x = [
        int.from_bytes(data[0:4], byteorder='big'),
        int.from_bytes(data[4:8], byteorder='big'),
        int.from_bytes(data[8:12], byteorder='big'),
        int.from_bytes(data[12:16], byteorder='big')
    ]
    
    # 32轮解密：轮密钥逆序使用 rk[31] -> rk[0]，与加密互为逆过程
    for i in range(31, -1, -1):
        t = x[1] ^ x[2] ^ x[3] ^ rk[i]
        t = sm4_sub_byte(t)
        t = sm4_l(t)
        x[0], x[1], x[2], x[3] = x[1], x[2], x[3], x[0] ^ t
    
    # 输出结果（大端序拼接）
    return (
        x[3].to_bytes(4, byteorder='big') +
        x[2].to_bytes(4, byteorder='big') +
        x[1].to_bytes(4, byteorder='big') +
        x[0].to_bytes(4, byteorder='big')
    )

# ==================== 填充函数 ====================
# PKCS5填充与SM4块大小(16字节)配合，确保数据长度为16的整数倍

def pkcs5_pad(data: bytes) -> bytes:
    """
    PKCS5填充：将数据长度补齐为16的整数倍
    填充值为填充字节数，严格对齐Java的PKCS5Padding
    例如：若差3字节，则填充 0x03 0x03 0x03
    :param data: 原始字节数据
    :return: 填充后的字节数据，长度为16的倍数
    """
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len] * pad_len)

def pkcs5_unpad(data: bytes) -> bytes:
    """
    去除PKCS5填充：根据最后一个字节的值移除填充内容
    对齐Java的解填充逻辑
    :param data: 带填充的数据（长度必须为16的倍数）
    :return: 去除填充后的原始数据
    :raises ValueError: 当填充长度无效时（不在1-16范围内）
    """
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        raise ValueError("无效的填充长度")
    return data[:-pad_len]


# ==================== 手机号加解密封装类 ====================

class MobileCipher:
    """
    手机号加解密工具类
    使用SM4/ECB + PKCS5 + Base64，100%对齐Java BouncyCastle实现
    确保Python加密结果可由Java解密，反之亦然
    """
    
    def __init__(self, secret_key: str):
        """
        初始化加解密器，校验密钥格式
        :param secret_key: 16字符的密钥字符串，UTF-8编码后须为16字节
        :raises ValueError: 密钥为空、长度不为16、或UTF-8编码后非16字节
        """
        if not secret_key or len(secret_key) != 16:
            raise ValueError("密钥必须为16位长度")
        # 密钥按UTF-8编码，与Java的getBytes(StandardCharsets.UTF_8)一致
        self.key = secret_key.encode('UTF-8')
        if len(self.key) != 16:
            raise ValueError("密钥UTF-8编码后必须为16字节")

    def encrypt_mobile(self, mobile: str) -> str:
        """
        加密单个手机号，输出Base64字符串
        流程：UTF-8编码 → PKCS5填充 → SM4/ECB加密 → Base64编码
        与Java的encryptMobile方法完全一致
        :param mobile: 明文手机号，如 "13800138000"
        :return: Base64编码的密文字符串
        :raises ValueError: 手机号为空
        :raises RuntimeError: 加密过程异常
        """
        if not mobile or len(mobile.strip()) == 0:
            raise ValueError("手机号为空")
        
        try:
            # 1. 手机号转为UTF-8字节，与Java编码方式一致
            mobile_bytes = mobile.encode('UTF-8')
            # 2. PKCS5填充，使长度为16的倍数
            padded_data = pkcs5_pad(mobile_bytes)
            # 3. 按16字节分块，ECB模式逐块加密
            encrypted = b""
            for i in range(0, len(padded_data), 16):
                block = padded_data[i:i+16]
                encrypted += sm4_encrypt_block(self.key, block)
            # 4. Base64编码，对应Java的Base64.encodeBase64String
            return base64.b64encode(encrypted).decode('UTF-8')
        except Exception as e:
            logger.error(f"加密手机号[{mobile}]失败", exc_info=e)
            raise RuntimeError(f"加密手机号失败: {mobile}") from e

    def decrypt_mobile(self, encrypt_mobile: str) -> str:
        """
        解密单个加密手机号，从Base64密文还原明文
        流程：Base64解码 → SM4/ECB解密 → 去PKCS5填充 → UTF-8解码
        与Java的decryptMobile方法完全一致
        :param encrypt_mobile: Base64编码的加密手机号字符串
        :return: 明文手机号
        :raises ValueError: 密文为空
        :raises RuntimeError: 解密过程异常（如密文损坏、密钥错误等）
        """
        if not encrypt_mobile or len(encrypt_mobile.strip()) == 0:
            raise ValueError("加密手机号为空")
        
        try:
            # 1. Base64解码得到密文字节
            encrypted_bytes = base64.b64decode(encrypt_mobile)
            # 2. 按16字节分块，ECB模式逐块解密
            decrypted = b""
            for i in range(0, len(encrypted_bytes), 16):
                block = encrypted_bytes[i:i+16]
                decrypted += sm4_decrypt_block(self.key, block)
            # 3. 去除PKCS5填充
            unpadded_data = pkcs5_unpad(decrypted)
            # 4. UTF-8解码为字符串
            return unpadded_data.decode('UTF-8')
        except Exception as e:
            logger.error(f"解密手机号[{encrypt_mobile}]失败", exc_info=e)
            raise RuntimeError(f"解密手机号失败: {encrypt_mobile}") from e

    def batch_encrypt_mobiles(self, mobiles: list) -> list:
        """
        批量加密手机号列表
        某个手机号加密失败时，该位置结果为None，不中断整个流程
        :param mobiles: 明文手机号列表
        :return: 加密结果列表，与输入一一对应，失败项为None
        """
        if not mobiles:
            logger.warning("批量加密的手机号列表为空")
            return []
        result = []
        for mobile in mobiles:
            try:
                result.append(self.encrypt_mobile(mobile))
            except Exception:
                result.append(None)
        return result

    def batch_decrypt_mobiles(self, encrypt_mobiles: list) -> list:
        """
        批量解密手机号列表
        某个密文解密失败时，该位置结果为None，不中断整个流程
        :param encrypt_mobiles: Base64加密手机号列表
        :return: 解密结果列表，与输入一一对应，失败项为None
        """
        if not encrypt_mobiles:
            logger.warning("批量解密的手机号列表为空")
            return []
        result = []
        for encrypt_mobile in encrypt_mobiles:
            try:
                result.append(self.decrypt_mobile(encrypt_mobile))
            except Exception:
                result.append(None)
        return result


# ==================== 业务辅助函数 ====================

def generate_and_encrypt_mobiles(initial_mobile: str, count: int, secret_key: str = None) -> dict:
    """
    根据初始手机号和数量，生成连续手机号并加密
    :param initial_mobile: 初始手机号，如 "13800138201"
    :param count: 数量
    :param secret_key: 16字符密钥，默认从环境变量 MOBILE_CIPHER_KEY 读取
    :return: {"mobiles": [...], "encrypted": [...]} 或 {"error": "..."}
    """
    import os
    key = secret_key or os.environ.get('MOBILE_CIPHER_KEY', 'xD4hM4iB1oQ3jG2c')
    try:
        cipher = MobileCipher(key)
        mobiles = create_mobile_list(initial_mobile, count)
        encrypted = cipher.batch_encrypt_mobiles(mobiles)
        return {'mobiles': mobiles, 'encrypted': encrypted}
    except Exception as e:
        return {'error': str(e)}


def create_mobile_list(initial_mobile: str, count: int) -> list:
    """
    根据初始手机号和数量，生成连续递增的手机号数组
    用于批量测试或生成客户数据时的手机号序列
    :param initial_mobile: 初始手机号字符串，如 "13800138151"
    :param count: 需要生成的数量，如 10
    :return: 手机号字符串列表，如 ["13800138151", "13800138152", ..., "13800138160"]
    """
    base = int(initial_mobile)
    return [str(base + i) for i in range(count)]

if __name__ == "__main__":
    # 密钥必须与 Java 端完全一致（16 字符），否则无法互通解密
    SECRET_KEY = "xD4hM4iB1oQ3jG2c"  # 替换为实际 Java 端使用的密钥
    cipher = MobileCipher(SECRET_KEY)
    
    # 生成连续手机号列表：从 13800138201 起，共 1 个
    mobiles = create_mobile_list("13800138201", 3)
    print(mobiles)
    # 批量加密手机号
    encrypt_mobiles = cipher.batch_encrypt_mobiles(mobiles)
    print(encrypt_mobiles)
    # 批量解密手机号
    decrypt_mobiles = cipher.batch_decrypt_mobiles(encrypt_mobiles)
    print(decrypt_mobiles)