from zimply.zimply import ZIMFile
from mako.template import Template
import re


class MyZIMFile(ZIMFile):
    def __init__(self, filename, encoding):
        super().__init__(filename, encoding)
    def on_get(self, location, template):
        """
        Process a HTTP GET request. An object is this class is created whenever
        an HTTP request is generated. This method is triggered when the request
        is of any type, typically a GET. This method will redirect the user,
        based on the request, to the index/search/correct page, or an error
        page if the resource is unavailable.
        """

        components = location.split("?")
        navigation_location = None
        is_article = True  # assume an article is requested, for now
        # if trying for the main page ...
        if location in ["/", "/index.htm", "/index.html",
                        "/main.htm", "/main.html"]:
            # ... return the main page as the article
            article = self.get_main_page()
            if article is not None:
                navigation_location = "main"
        else:
            # The location is given as domain.com/namespace/url/parts/ ,
            # as used in the ZIM link or, alternatively, as domain.com/page.htm
            _, namespace, *url_parts = location.split("/")

            # are we dealing with an address bar request, eg. /article_name.htm
            if len(namespace) > 1:
                url = namespace  # the namespace is then the URL
                namespace = "A"  # and the namespace is an article
            else:
                # combine all the url parts together again
                url = "/".join(url_parts)
            # get the desired article
            article = self.get_article_by_url(namespace, url)
            # we have an article when the namespace is A
            # (i.e. not a photo, etc.)
            is_article = (namespace == "A")

        # from this point forward, "article" refers to an element in the ZIM
        # database whereas is_article refers to a Boolean to indicate whether
        # the "article" is a true article, i.e. a webpage
        success = True  # assume the request succeeded
        search = False  # assume we do not have a search
        keywords = ""  # the keywords to search for

        if not article:
            success = False

        template = Template(template)
        result = body = head = title = ""  # preset all template variables
        if success:  # if succesdsful, i.e. we found the requested resource
            

            if not navigation_location:  # check if the article location is set
                    # if not, default to "browse" (non-search, non-main page)
                    navigation_location = "browse"

            
            if is_article:
                text = article.data  # we have an actual article
                # decode its contents into a string using its encoding
                text = text.decode(encoding='utf-8')
                # retrieve the body from the ZIM article
                m = re.search(r"<body.*?>(.*?)</body>", text, re.S)
                body = m.group(1) if m else ""
                # retrieve the head from the ZIM article
                m = re.search(r"<head.*?>(.*?)</head>", text, re.S)
                head = m.group(1) if m else ""
                # retrieve the title from the ZIM article
                m = re.search(r"<title.*?>(.*?)</title>", text, re.S)
                title = m.group(1) if m else ""
            else:
                # just a binary blob, so use it as such
                result = article.data
            

        else:  # if we did not achieve success
            title = "Page 404"
            body = "requested resource not found"

        if not result:  # if the result hasn't been prefilled ...
            result = template.render(location=navigation_location, body=body,
                                     head=head, title=title)  # render template
            return bytes(result, encoding='utf-8')
        else:
            # if result is already filled, push it through as-is
            # (i.e. binary resource)
            return result
