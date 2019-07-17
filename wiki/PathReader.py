from struct import unpack
from django.conf import settings


def get_path(pair_id, complexity, bytes_count=4):
    if complexity not in settings.LEVEL_FILE_NAMES_V2.keys():
        return []

    offset_file = open(settings.LEVEL_FILE_NAMES_V2[complexity], 'rb')
    offset_file.seek((pair_id * 3 + 1) * bytes_count)

    start_vertex = unpack(settings.UNPACK_FORMAT, offset_file.read(4))[0]
    finish_vertex = unpack(settings.UNPACK_FORMAT, offset_file.read(4))[0]
    offset = unpack(settings.UNPACK_FORMAT, offset_file.read(4))[0]

    path_file = open(settings.LEVEL_PATH_FILE_NAMES_V2[complexity], 'rb')
    path_file.seek(offset)

    path_length = unpack(settings.UNPACK_FORMAT, path_file.read(4))[0]
    path = [start_vertex]
    path += [unpack(settings.UNPACK_FORMAT, path_file.read(4))[0] for i in range(path_length)]
    path.append(finish_vertex)

    return path
