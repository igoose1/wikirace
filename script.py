import zimply
import time
import re
import urllib.parse as parse
import sys


def get_links_from_html(data):
    pats = re.findall(r'href="[^""]*.html"', data)
    links = []
    for elem in pats:
        elem = elem[6:-1]
        if elem.startswith('http'):
            continue
        else:
            links.append(parse.unquote(elem))
    return links


def int_to_bytes(x):
    b1 = ((x & (255 << 24)) >> 24)
    b2 = ((x & (255 << 16)) >> 16)
    b3 = ((x & (255 << 8)) >> 8)
    b4 = (x & 255)
    return bytes([b1, b2, b3, b4])


def generate_graph(x, zim_name):
    wikipedia = zimply.zimply.ZIMFile(zim_name, 'utf-8')
    articleCount = wikipedia.header_fields['articleCount']
    
    edges = open('edges' + str(x), 'wb')
    offset = open('offset' + str(x), 'wb')
    off = 0    
    
    start_time = time.time()
    block = articleCount // 16
    start = x * block
    fin = (x + 1) * block
    if x == 15:
        fin = articleCount
    for i in range(start, fin):
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
                if entry is None:
                    continue
                while 'redirectIndex' in entry.keys():
                    index = entry['redirectIndex']
                    entry = wikipedia.read_directory_entry_by_index(index)
                edges.write(int_to_bytes(index))
                cnt += 1
        offset.write(int_to_bytes(off))
        off += cnt * 4
        
    offset.write(int_to_bytes(off))
    offset.close()
    edges.close()
    print(time.time() - start_time)

generate_graph(int(sys.argv[1]), sys.argv[2])



