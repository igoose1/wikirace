# "this ugly hack" is needed for django working:
# Zimply tryes to log in our directory; lib also impements own settings
# that crashes Django.  The 'monkey.patch_all' and 'logging.baseConfig'
# is  thecause of  problems,  so we just override them, before  import
# zimply
from gevent import monkey
monkey.patch_all = lambda *_: None

import logging
saved_basicConfig = logging.basicConfig
logging.basicConfig = lambda *_, **__: None

import zimply.zimply

logging.baseConfig = saved_basicConfig

from django.conf import settings
from random import randrange
from byte_convert import bytes_to_int
import os

def parse_url(url):
    namespace, *url_parts = url.split("/")
    if len(namespace) > 1:
        return "A", namespace
    else:
        return namespace, "/".join(url_parts)

class Article:
    def __init__(self, entry, zim_file):
        self._zim_file = zim_file
        self._entry = entry
        self._article_cashed = None

    def follow_redirect(self, max_redirects_count=10):
        self._article_cashed = None
        redirect_id = 0
        while self.is_redirecting:
            redirect_index = self._entry['redirectIndex']
            self._entry = self._zim_file.read_directory_entry_by_index(redirect_index)
            redirect_id += 1
            if redirect_id == max_redirects_count:
                break
            
    def check_and_follow_redirect(self, max_redirects_count=10):
        self.follow_redirect(max_redirects_count)
        return self.is_redirecting
        
    @property
    def is_redirecting(self):
        return 'redirectIndex' in self._entry.keys()
            
    @property
    def article(self):
        if self._article_cashed is None:
            article = self._zim_file._get_article_by_index(self.index, follow_redirect=False)
            self._article_cashed = article
        return self._article_cashed

    @property
    def index(self):
        return self._entry['index']

    @property
    def content(self):
        return self.article.data

    @property
    def namespace(self):
        return self._entry['namespace']

    @property
    def mimetype(self):
        return self._zim_file.mimetype_list[self._entry['mimetype']]

    @property
    def title(self):
        return self._entry['title']

    @property
    def url(self):
        return self._entry['url']


class ZIMFile:
    def __init__(self, filename, encoding='utf-8'):
        self._impl = zimply.zimply.ZIMFile(filename, encoding)
        self._article_indexes = open(settings.WIKI_ARTICLES_INDEX_FILE_PATH, 'rb')
        self._good_article_count = os.path.getsize(settings.WIKI_ARTICLES_INDEX_FILE_PATH) // 4

    def random_article(self):
        offset = randrange(0, self._good_article_count) * 4
        self._article_indexes.seek(offset)
        index = bytes_to_int(self._article_indexes.read(4))
        return self[index]

    def __getitem__(self, key):
        if isinstance(key, int):
            entry = self._impl.read_directory_entry_by_index(key)
            return Article(entry, self._impl)
        else:
            namespace, url = parse_url(key)
            entry, idx = self._impl._get_entry_by_url(namespace, url)
            return Article(entry, self._impl)

    def __len__(self):
        return len(self._impl)

    def close(self):
        self._impl.close()
        self._article_indexes.close()
