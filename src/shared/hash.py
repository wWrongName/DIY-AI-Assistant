import hashlib


def md5_hash(input_string: str) -> str:
    md5 = hashlib.md5()
    md5.update(input_string.encode('utf-8'))
    return md5.hexdigest()
