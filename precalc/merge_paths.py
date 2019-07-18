import os
from struct import unpack, pack
import sys


def merge(files_count, path_to_dir, difficulty):
    with open(os.path.join(path_to_dir, difficulty + "_paths"), 'wb') as paths_file:
        offset_count = 0
        offsets = []
        for i in range(1, files_count + 1):
            iter_offset_file = open(os.path.join(path_to_dir, difficulty + str(i)), 'rb')
            length = unpack(">I", iter_offset_file.read(4))[0]
            iter_paths_file = open(os.path.join(path_to_dir, difficulty + str(i) + "_paths"), 'rb')
            for _ in range(length):
                start_vertex = unpack('>I', iter_offset_file.read(4))[0]
                finish_vertex = unpack('>I', iter_offset_file.read(4))[0]
                offset = unpack('>I', iter_offset_file.read(4))[0]
                iter_paths_file.seek(offset)
                path_length = unpack('>I', iter_paths_file.read(4))[0]
                path = []
                path += [unpack('>I', iter_paths_file.read(4))[0] for i in range(path_length)]
                paths_file.write(pack('>i', path_length))
                for v in path:
                    paths_file.write(pack('>i', v))

                offset += offset_count
                offsets.append((start_vertex, finish_vertex, offset))
            offset_count = offset + path_length
            iter_paths_file.close()
            iter_offset_file.close()
    with open(os.path.join(path_to_dir, difficulty + "_paths"), 'wb') as offset_file:
        offset_file.write(pack('>i', len(offsets)))
        for i in offsets:
            offset_file.write(pack('>i', i))


if __name__ == "__main__":
    merge(*sys.argv[1:])
