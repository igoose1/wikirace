from zimply.zimply import ZIMFile


class MyZIMFile(ZIMFile):
    def __init__(self, filename, encoding='utf-8'):
        super().__init__(filename, encoding)
        
    # get_by_url will return an Article by url
    # Article = namedtuple("Article", ["data", "namespace", "mimetype"])
    # Article.data: bytes
    # Article.namespace: namespace as string (example: "A", "I")
    # Article.mimetype: mimetype as string
    def get_by_url(self, relative_url):
        _, namespace, *url_parts = relative_url.split("/")
        
        url=None
        if len(namespace) > 1:
            url = namespace 
            namespace = "A" 
        else:
            url = "/".join(url_parts)
        article = self.get_article_by_url(namespace, url)
        
        return article
