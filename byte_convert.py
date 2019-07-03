def int_to_bytes(src: int, bytes_count: int = 4):
    """
    Converts int to fixed count of bytes
    :param src: int to convert
    :param bytes_count: size of result
    :return: converted bytes
    """
    res = []
    for i in range(bytes_count):
        res.append(src % 256)
        src = src // 256
    res.reverse()
    return bytes(res)


def bytes_to_int(src: bytes):
    """
    Converts bytes to int
    :param src: bytes to convert
    :return: resulted int
    """
    res = 0
    for i in range(len(src)):
        res <<= 8
        res |= src[i]
    return res
