from struct import unpack
from .ZIMFile import ZIMFile
from django.conf import settings
from precalc.merge_paths import read_int


def get_path(pair_id, complexity, bytes_count=4):
    if complexity not in settings.LEVEL_FILE_NAMES_V2.keys():
        return []

    with open(settings.LEVEL_FILE_NAMES_V2[complexity], 'rb') as offset_file:
        offset_file.seek((pair_id * 3 + 1) * bytes_count)
        start_vertex = read_int(offset_file)
        finish_vertex = read_int(offset_file)
        offset = read_int(offset_file)

    with open(settings.LEVEL_PATH_FILE_NAMES_V2[complexity], 'rb') as path_file:
        path_file.seek(offset)
        path_length = read_int(path_file)
        path = [start_vertex]
        path += [read_int(path_file) for i in range(path_length)]
        path.append(finish_vertex)

    return path
