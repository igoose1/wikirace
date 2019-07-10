from byte_convert import bytes_to_int


def get_path(pair_id, complexity, bytes_count=4):
    path_file = open('data/ok1/{}_paths'.format(complexity), 'rb')
    offset_file = open('data/ok1/{}'.format(complexity), 'rb')

    offset_file.seek(bytes_count * (3 * pair_id + 1))

    start_vertex = bytes_to_int(offset_file.read(bytes_count))
    finish_vertex = bytes_to_int(offset_file.read(bytes_count))

    offset = bytes_to_int(offset_file.read(bytes_count))
    path_file.seek(offset)

    path_length = bytes_to_int(path_file.read(bytes_count))
    print(path_length)
    path = [start_vertex]

    for _ in range(path_length):
        current_vertex = bytes_to_int(path_file.read(bytes_count))
        path.append(current_vertex)

    path.append(finish_vertex)
    return path
