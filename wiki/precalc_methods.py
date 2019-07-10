from random import randrange
import struct

N = 5054753


def write_to_files(pair_file_name, path_file_name, pairs, paths):
    file = open(pair_file_name, 'wb')
    path_file = open(path_file_name, 'wb')
    file.write(struct.pack('>i', len(pairs)))
    off = 0
    for i in range(len(pairs)):
        p = pairs[i]
        file.write(struct.pack('>i', p[0]))
        file.write(struct.pack('>i', p[1]))
        file.write(struct.pack('>i', off))
        path_file.write(struct.pack('>i', len(paths[i])))
        off += 4
        for v in paths[i]:
            path_file.write(struct.pack('>i', v))
            off += 4
    file.close()
    path_file.close()


def choose_start_vertex(reader):
    page_id = randrange(0, N)
    while reader.edges_count(page_id) < 5:
        page_id = randrange(0, N)
    print('start vertex', page_id, flush=True)
    return page_id


def only_digits(name):
    for c in name:
        if ord(c) < ord('0') or ord(c) > ord('9'):
            return False
    return True


def includes_a_year(name):
    return ('год' in name) or ('Год' in name)