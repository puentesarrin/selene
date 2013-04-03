# -*- coding: utf-8 *-*
import misaka
import postmarkup
import re

from docutils import core
from docutils.writers.html4css1 import Writer, HTMLTranslator
from HTMLParser import HTMLParser
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\:\;\-/<=>?@\[\\\]^_`{|},.]+')


def get_slug(input_text, delim=u"-", stop_words=[]):
    result = []
    for word in _punct_re.split(input_text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word and word not in stop_words:
            result.append(word)
    return unicode(delim.join(result))

_whitespace = re.compile('\s+')


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
        return _whitespace.sub(' ', self.out).strip()


def get_plain_from_html(html):
    parser = HTMLStripTags()
    parser.feed(html)
    return parser.value()


class CleanedHTMLTranslator(HTMLTranslator):

    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head = ""
        self.head_prefix = ['', '', '', '', '']
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        self.fragment = self.body

_w = Writer()
_w.translator_class = CleanedHTMLTranslator


def get_html_from_rst(rst):
    return core.publish_string(rst, writer=_w)


def get_html_from_md(md):
    return misaka.html(md)


_bbcode_markup = postmarkup.create()


def get_html_from_bbcode(bbcode):
    return _bbcode_markup(bbcode)


def get_html_and_plain(text, text_input_type):
    if text_input_type == 'html':
        return text, get_plain_from_html(text)
    elif text_input_type == 'md':
        html = get_html_from_md(text)
        return html, get_plain_from_html(html)
    elif text_input_type == 'rst':
        html = get_html_from_rst(text)
        return html, get_plain_from_html(html)
    elif text_input_type == 'bbcode':
        html = get_html_from_bbcode(text)
        return html, _bbcode_markup.cleanup_html(text).strip()
    return text, text
