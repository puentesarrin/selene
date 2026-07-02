import re
from collections.abc import Sequence
from html import escape
from html.parser import HTMLParser
from importlib import import_module
from typing import Any

from slugify import slugify

from selene.constants import TextType

WHITESPACE_RE = re.compile(r'\s+')


def get_slug(input_text: str, stop_words: Sequence[str] | None = None) -> str:
    return slugify(input_text, stopwords=stop_words or [])


class HTMLStripTags(HTMLParser):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.out = ''

    def handle_data(self, data: str) -> None:
        self.out += data

    def handle_entityref(self, name: str) -> None:
        self.out += f'&{name};'

    def handle_charref(self, name: str) -> None:
        return self.handle_entityref('#' + name)

    def value(self) -> str:
        return WHITESPACE_RE.sub(' ', self.out).strip()


def get_plain_from_html(html: str | None) -> str:
    parser = HTMLStripTags()
    parser.feed(html or '')
    return parser.value()


class TextPlainFormatter:
    def html(self, input_text: str) -> str:
        return input_text

    def plain(self, input_text: str) -> str:
        return input_text

    def process(self, input_text: str) -> tuple[str, str]:
        return self.html(input_text), self.plain(input_text)


class HTMLFormatter(TextPlainFormatter):
    def plain(self, input_text: str) -> str:
        return get_plain_from_html(input_text)


class MarkupLanguageFormatter(HTMLFormatter):
    def process(self, input_text: str) -> tuple[str, str]:
        html = self.html(input_text)
        if isinstance(html, bytes):
            html = html.decode('utf-8')
        return html, self.plain(html)


class MarkdownFormatter(MarkupLanguageFormatter):
    def html(self, input_text: str) -> str:
        mistune = _import_optional_dependency('mistune', 'Markdown')
        return mistune.html(input_text)


class reStructuredTextFormatter(MarkupLanguageFormatter):
    def __init__(self) -> None:
        _import_optional_dependency('docutils', 'reStructuredText')
        from docutils.writers.html4css1 import HTMLTranslator

        class CleanedHTMLTranslator(HTMLTranslator):
            def __init__(self, document):
                super().__init__(document)
                self.head = ''
                self.head_prefix = ['', '', '', '', '']
                self.body_prefix = []
                self.body_suffix = []
                self.stylesheet = []

            def visit_document(self, node):
                pass

            def depart_document(self, node):
                self.fragment = self.body

        self.translator_class = CleanedHTMLTranslator

    def html(self, input_text: str) -> str:
        docutils_core = _import_optional_dependency('docutils.core', 'reStructuredText')
        from docutils.writers.html4css1 import Writer

        writer = Writer()
        writer.translator_class = self.translator_class
        return docutils_core.publish_string(input_text, writer=writer).decode('utf-8')


class BBCodeFormatter(MarkupLanguageFormatter):
    def html(self, input_text: str) -> str:
        bbcode = _import_optional_dependency('bbcode', 'BBCode')
        parser = bbcode.Parser()
        return parser.format(input_text)


class TextileFormatter(MarkupLanguageFormatter):
    def html(self, input_text: str) -> str:
        textile = _import_optional_dependency('textile', 'Textile')
        return textile.textile(input_text)


class MediaWikiFormatter(MarkupLanguageFormatter):
    def html(self, input_text: str) -> str:
        return '<pre>{}</pre>'.format(escape(input_text))


class CreoleFormatter(MarkupLanguageFormatter):
    def html(self, input_text: str) -> str:
        creole = _import_optional_dependency('creole', 'Creole')
        return creole.creole2html(input_text)


class TextConverter:
    def __init__(self, formatter: type[TextPlainFormatter]):
        self.formatter = formatter

    def __call__(self, input_text: str) -> tuple[str, str]:
        return self.formatter().process(input_text)


def _import_optional_dependency(module_name: str, text_type: str) -> Any:
    try:
        return import_module(module_name)
    except ImportError as exc:
        raise RuntimeError(
            f'{text_type} rendering requires the optional {module_name!r} package. '
            f'Install Selene with the matching extra or add {module_name!r} to your environment.'
        ) from exc


def get_html_and_plain(input_text: str, input_text_type: str) -> tuple[str, str]:
    text_type = TextType(input_text_type)
    return TextConverter(FORMATTER_MAP[text_type])(input_text)


FORMATTER_MAP = {
    TextType.TEXT: TextPlainFormatter,
    TextType.HTML: HTMLFormatter,
    TextType.MD: MarkdownFormatter,
    TextType.RST: reStructuredTextFormatter,
    TextType.BBCODE: BBCodeFormatter,
    TextType.TEXTILE: TextileFormatter,
    TextType.MEDIAWIKI: MediaWikiFormatter,
    TextType.CREOLE: CreoleFormatter,
}
