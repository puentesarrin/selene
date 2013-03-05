# -*- coding: utf-8 *-*
import cgi
import urllib
import urlparse


class Url(object):

    def __init__(self, url):
        (self.scheme, self.netloc, self.path, self.params, self.query,
            self.fragment) = urlparse.urlparse(url)
        self.args = dict(cgi.parse_qsl(self.query))

    def __str__(self):
        self.query = urllib.urlencode(self.args)
        return urlparse.urlunparse((self.scheme, self.netloc, self.path,
                                    self.params, self.query, self.fragment))
