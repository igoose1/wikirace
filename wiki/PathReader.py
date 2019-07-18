from struct import unpack
from .ZIMFile import ZIMFile
from django.conf import settings


def get_path(pair_id, complexity, bytes_count=4):
    if complexity not in settings.LEVEL_FILE_NAMES_V2.keys():
        return []

    with open(settings.LEVEL_FILE_NAMES_V2[complexity], 'rb') as offset_file:
        offset_file.seek((pair_id * 3 + 1) * bytes_count)
        start_vertex = unpack('>I', offset_file.read(4))[0]
        finish_vertex = unpack('>I', offset_file.read(4))[0]
        offset = unpack('>I', offset_file.read(4))[0]

    with open(settings.LEVEL_PATH_FILE_NAMES_V2[complexity], 'rb') as path_file:
        path_file.seek(offset)
        path_length = unpack('>I', path_file.read(4))[0]
        path = [start_vertex]
        path += [unpack('>I', path_file.read(4))[0] for i in range(path_length)]
        path.append(finish_vertex)

    return path
