# -*- coding: utf-8 *-*
import re

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


class TextPlainFormatter(object):

    def html(self, input_text):
        return input_text

    def plain(self, input_text):
        return input_text

    def process(self, input_text):
        return self.html(input_text), self.plain(input_text)


class HTMLFormatter(TextPlainFormatter):

    def plain(self, input_text):
        return get_plain_from_html(input_text)


class MarkupLanguageFormatter(HTMLFormatter):

    def process(self, input_text):
        html = self.html(input_text)
        return html, self.plain(html)


class MarkdownFormatter(MarkupLanguageFormatter):

    def html(self, input_text):
        import misaka
        return misaka.html(input_text)


class reStructuredTextFormatter(MarkupLanguageFormatter):

    def __init__(self):
        from docutils.writers.html4css1 import HTMLTranslator

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

        self.translator_class = CleanedHTMLTranslator

    def html(self, input_text):
        from docutils import core
        from docutils.writers.html4css1 import Writer
        writer = Writer()
        writer.translator_class = self.translator_class
        return core.publish_string(input_text, writer=writer)


class BBCodeFormatter(MarkupLanguageFormatter):

    def html(self, input_text):
        import postmarkup
        bbcode_markup = postmarkup.create()
        return bbcode_markup(input_text)


class TextileFormatter(MarkupLanguageFormatter):

    def html(self, input_text):
        import textile
        return textile.textile(input_text)


class MediaWikiFormatter(MarkupLanguageFormatter):

    def html(self, input_text):
        import mediawiki
        return mediawiki.wiki2html(input_text, False)


class CreoleFormatter(MarkupLanguageFormatter):

    def html(self, input_text):
        import creole
        return creole.creole2html(input_text)


class TextConverter(object):

    def __init__(self, formatter):
        self.formatter = formatter

    def __call__(self, input_text):
        return self.formatter().process(input_text)


_formatter_map = {'text': TextPlainFormatter,
                  'html': HTMLFormatter,
                  'md': MarkdownFormatter,
                  'rst': reStructuredTextFormatter,
                  'bbcode': BBCodeFormatter,
                  'textile': TextileFormatter,
                  'mediawiki': MediaWikiFormatter,
                  'creole': CreoleFormatter}


def get_html_and_plain(input_text, input_text_type):
    return TextConverter(_formatter_map[input_text_type])(input_text)
