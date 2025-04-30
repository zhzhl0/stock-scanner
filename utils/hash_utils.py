import hashlib


def generate_hash(input_string: str) -> str:
    """
    生成字符串的哈希值
    :param input_string: 输入字符串
    :return: 哈希值
    """
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode("utf-8"))
    return md5_hash.hexdigest()
