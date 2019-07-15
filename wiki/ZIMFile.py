# "this ugly hack" is needed for django working:
# Zimply tryes to log in our directory; lib also impements own settings
# that crashes Django. The 'monkey.patch_all' and 'logging.baseConfig'
# is the cause of problems, so we just override them, before import
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
from wiki.file_holder import file_holder

BLOCK_SIZE = 4


def parse_url(url):
    namespace, *url_parts = url.split("/")
    if len(namespace) > 1:
        return ZIMFile.NAMESPACE_ARTICLE, namespace
    else:
        return namespace, "/".join(url_parts)


class Article:
    def __init__(self, entry, zim_file):
        self._zim_file = zim_file
        self._entry = entry
        self._article_cached = None
        if self._entry is None:
            self._entry = dict()

    def follow_redirect(self, max_redirects_count=10):
        self._article_cached = None
        redirect_counter = 0
        entry = self._entry
        while 'redirectIndex' in entry.keys():
            redirect_index = entry['redirectIndex']
            entry = self._zim_file.read_directory_entry_by_index(
                redirect_index)
            redirect_counter += 1
            if redirect_counter == max_redirects_count:
                break
        return Article(entry, self._zim_file)

    @property
    def is_empty(self):
        return self.index == -1

    @property
    def is_redirecting(self):
        return 'redirectIndex' in self._entry.keys()

    @property
    def _article(self):
        if self._article_cached is None:
            article = self._zim_file._get_article_by_index(
                self.index, follow_redirect=False)
            self._article_cached = article
        return self._article_cached

    @property
    def index(self):
        return self._entry.get('index', -1)

    @property
    def content(self):
        return self._article.data

    @property
    def namespace(self):
        return self._entry.get('namespace', '')

    @property
    def mimetype(self):
        return self._zim_file.mimetype_list[self._entry.get('mimetype', 0)]

    @property
    def title(self):
        return self._entry.get('title', '')

    @property
    def url(self):
        return self._entry.get('url', '')


@file_holder
class ZIMFile:
    NAMESPACE_ARTICLE = "A"

    def __init__(self, filename, index_filename, encoding='utf-8'):
        self._impl = None
        self._article_indexes = None
        self._impl = self._add_file(zimply.zimply.ZIMFile(filename, encoding))
        self._article_indexes = self._open_file(index_filename, "rb")
        self._good_article_count = os.path.getsize(index_filename) // BLOCK_SIZE

    def random_article(self):
        offset = randrange(0, self._good_article_count) * BLOCK_SIZE
        self._article_indexes.seek(offset)
        index = bytes_to_int(self._article_indexes.read(BLOCK_SIZE))
        return self[index]

    def __getitem__(self, key):
        if isinstance(key, int):
            entry = self._impl.read_directory_entry_by_index(key)
        else:
            namespace, url = parse_url(key)
            entry, idx = self._impl._get_entry_by_url(namespace, url)
        return Article(entry, self._impl)

    def __len__(self):
        return len(self._impl)
