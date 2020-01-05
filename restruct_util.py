import sys
from struct import pack, unpack
path1 = sys.argv[1]
path2 = sys.argv[2]
SIZE = 4


with open(path1, 'rb') as file1, open(path2, 'wb') as file2:
    data = file1.read(16384)
    while len(data) > 0:
        file2.write(pack(
                    "<" + "I" * (len(data) // 4),
                    *unpack(
                        ">" + "I" * (len(data) // 4),
                        data
                        ))
                    )
        data = file1.read(16384)

