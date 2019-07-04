
# TODO: describe this ugly hack
from gevent import monkey
monkey.patch_all = lambda *_: None

import logging
saved_basicConfig = logging.basicConfig
logging.basicConfig = lambda *_, **__: None

from zimply.zimply import ZIMFile

logging.baseConfig = saved_basicConfig


class MyZIMFile(ZIMFile):
    def __init__(self, filename, encoding='utf-8'):
        super().__init__(filename, encoding)
    def get_by_index(self, index:int):
        article = None
        try:
            article = self._get_article_by_index(index)
        except:
            pass
        return article
    # get_by_url will return an Article by url
    # Article = namedtuple("Article", ["data", "namespace", "mimetype"])
    # Article.data: bytes
    # Article.namespace: namespace as string (example: "A", "I")
    # Article.mimetype: mimetype as string
    def get_by_url(self, relative_url):
        _, namespace, *url_parts = relative_url.split("/")
        
        url = None
        if len(namespace) > 1:
            url = namespace 
            namespace = "A" 
        else:
            url = "/".join(url_parts)
        article = None
        try:
            article = self.get_article_by_url(namespace, url)
        except:
            pass
        
        return article
