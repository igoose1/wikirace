from struct import unpack
from .ZIMFile import ZIMFile
from django.conf import settings


def get_path(pair_id, complexity, bytes_count=4):
    with ZIMFile(settings.WIKI_ZIMFILE_PATH, settings.WIKI_ARTICLES_INDEX_FILE_PATH
                 ) as zim_file:
        if complexity not in settings.LEVEL_FILE_NAMES_V2.keys():
            print('complexity', complexity)
            return []
    
        offset_file = open(settings.LEVEL_FILE_NAMES_V2[complexity], 'rb')
        offset_file.seek((pair_id * 3 + 1) * bytes_count)
        
        start_vertex = unpack('>I', offset_file.read(4))[0]
        finish_vertex = unpack('>I', offset_file.read(4))[0]
        offset = unpack('>I', offset_file.read(4))[0]
    
        path_file = open(settings.LEVEL_PATH_FILE_NAMES_V2[complexity], 'rb')
        path_file.seek(offset)
    
        path_length = unpack('>I', path_file.read(4))[0]
        path = [start_vertex]
    
        for _ in range(path_length):
            path.append(unpack('>I', path_file.read(4))[0])
        path.append(finish_vertex)

    return path