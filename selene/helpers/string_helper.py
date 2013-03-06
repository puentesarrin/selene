# -*- coding: utf-8 *-*
import re

from HTMLParser import HTMLParser
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\:\;\-/<=>?@\[\\\]^_`{|},.]+')


def get_slug(input_text, delim=u"-"):
    result = []
    for word in _punct_re.split(input_text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))

whitespace = re.compile('\s+')


class HTMLStripTags(HTMLParser):

    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.out = ""

    def handle_data(self, data):
        self.out += data

    def handle_entityref(self, name):
        self.out += '&%s;' % name

    def handle_charref(self, name):
        return self.handle_entityref('#' + name)

    def value(self):
        return whitespace.sub(' ', self.out).strip()


def get_plain(html):
    parser = HTMLStripTags()
    parser.feed(html)
    return parser.value()
