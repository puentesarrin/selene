# -*- coding: utf-8 *-*
import re

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator
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


def get_plain_from_html(html):
    parser = HTMLStripTags()
    parser.feed(html)
    return parser.value()


class NoHeaderHTMLTranslator(HTMLTranslator):

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.doctype = ("")
        self.head_prefix_template = ("")
        self.meta = [""]
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

_w = Writer()
_w.translator_class = NoHeaderHTMLTranslator


def get_html_from_rst(rst):
    return core.publish_string(rst, writer=_w)
