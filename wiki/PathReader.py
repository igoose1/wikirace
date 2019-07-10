from ZIMFile import ZIMFile
from struct import unpack
from django.conf import settings


def get_path(pair_id, complexity, bytes_count=4):
    path_file = open('data/ok1/{}_paths'.format(complexity), 'rb')
    offset_file = open('data/ok1/{}'.format(complexity), 'rb')

    offset_file.seek(bytes_count * (3 * pair_id + 1))

    start_vertex = unpack('>I', offset_file.read(bytes_count))[0]
    finish_vertex = unpack('>I', offset_file.read(bytes_count))[0]

    offset = unpack('>I', offset_file.read(bytes_count))[0]
    path_file.seek(offset)

    path_length = unpack('>I', path_file.read(bytes_count))[0]
    path = [start_vertex]

    for _ in range(path_length):
        current_vertex = unpack('>I', path_file.read(bytes_count))[0]
        path.append(current_vertex)

    path.append(finish_vertex)
    return path


def page_names_in_path(pair_id, complexity, bytes_count=4):
    path = get_path(pair_id, complexity, bytes_count)
    # zim_file = ZIMFile(settings.WIKI_ZIMFILE_PATH,
    #                    settings.WIKI_ARTICLES_INDEX_FILE_PATH)
    zim_file = ZIMFile('/mnt/e/wiki/wikipedia_ru.zim',
                       '/mnt/e/wiki/git/wikirace/wiki/data/good_articles_list')
    for i in range(len(path)):
        path[i] = zim_file[path[i]].title
    return path


i = int(input())
c = input()
print(page_names_in_path(i, c))
