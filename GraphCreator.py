import zimply
import time
import re
import urllib.parse as parse
import sys
from django.conf import settings


def get_links_from_html(data):
    # If you need to extract graph from category (not full wikipedia)
    # remove '.html'
    pats = re.findall(r'href="[^""]*.html"', data)
    links = []
    for elem in pats:
        elem = elem[6:-1]
        if not elem.startswith('http'):
            links.append(parse.unquote(elem))
    return links


def int_to_bytes(x):
    b1 = ((x & (255 << 24)) >> 24)
    b2 = ((x & (255 << 16)) >> 16)
    b3 = ((x & (255 << 8)) >> 8)
    b4 = (x & 255)
    return bytes([b1, b2, b3, b4])


def generate_graph(x, threads_num, output_dir):
    if x < 0 or x >= threads_num:
        return

    wikipedia = zimply.zimply.ZIMFile(settings.WIKI_ZIMFILE_PATH, 'utf-8')
    article_count = wikipedia.header_fields['articleCount']

    used = [-1] * article_count
    it_id = 0

    edges = open(output_dir + 'edges' + str(x), 'wb')
    offset = open(output_dir + 'offset' + str(x), 'wb')
    off = 0

    start_time = time.time()
    block = article_count // threads_num
    start = x * block
    fin = (x + 1) * block

    if x == threads_num - 1:
        fin = article_count
    for i in range(start, fin):
        if i % 1000 == 0:
            print(i, "files are ready")
        current_article = wikipedia.read_directory_entry_by_index(i)
        if 'redirectIndex' in current_article.keys():
            offset.write(int_to_bytes(off))
            continue
        cnt = 0
        if current_article['namespace'] == 'A':
            data = wikipedia._read_blob(current_article['clusterNumber'], current_article['blobNumber'])
            links = get_links_from_html(data.decode('utf-8'))
            for link in links:
                entry, index = wikipedia._get_entry_by_url('A', link)
                it_id += 1
                while (entry is not None and entry['namespace'] == 'A' and
                       'redirectIndex' in entry.keys() and
                       used[index] != it_id):
                    used[index] = it_id
                    index = entry['redirectIndex']
                    entry = wikipedia.read_directory_entry_by_index(index)
                if entry is None or entry['namespace'] != 'A':
                    continue
                edges.write(int_to_bytes(index))
                cnt += 1
        offset.write(int_to_bytes(off))
        off += cnt * 4

    offset.write(int_to_bytes(off))
    offset.close()
    edges.close()
    print('Time of execution:', time.time() - start_time)


'''
in command line:
1 argument - id of thread (from 0 to (number_of_threads - 1))
2 argument - number of threads
3 argument - where to put result
'''

generate_graph(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
