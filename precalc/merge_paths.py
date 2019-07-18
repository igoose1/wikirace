import os
from struct import unpack, pack
import sys


def read_int(file):
    return unpack('>I', file.read(4))[0]


def write_int(file, *number):
    for i in number:
        file.write(pack(">I", i))


def merge(files_count, path_to_dir, difficulty):
    with open(os.path.join(path_to_dir, difficulty + "_paths"), 'wb') as paths_file:
        offsets = []
        for i in range(1, int(files_count) + 1):
            with open(os.path.join(path_to_dir, difficulty + str(i)), 'rb') as iter_offset_file,\
                    open(os.path.join(path_to_dir, difficulty + str(i) + "_paths"), 'rb') as iter_paths_file:
                length = read_int(iter_offset_file)
                for _ in range(length):
                    start_vertex = read_int(iter_offset_file)
                    finish_vertex = read_int(iter_offset_file)
                    offset = read_int(iter_offset_file)
                    iter_paths_file.seek(offset)
                    path_length = read_int(iter_paths_file)
                    path = [read_int(iter_paths_file) for _ in range(path_length)]
                    offset = paths_file.tell()
                    write_int(paths_file, path_length)
                    for v in path:
                        write_int(paths_file, v)
                    offsets.append((start_vertex, finish_vertex, offset))
                iter_paths_file.close()
                iter_offset_file.close()
    with open(os.path.join(path_to_dir, difficulty), 'wb') as offset_file:
        write_int(offset_file, len(offsets))
        for offset in offsets:
            write_int(offset_file, *offset)


if __name__ == "__main__":
    merge(*sys.argv[1:])
