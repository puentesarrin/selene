# -*- coding: utf-8 *-*
import re
from unicodedata import normalize

_punct_re = re.compile(r'[\t !"#$%&\'()*\:\;\-/<=>?@\[\\\]^_`{|},.]+')


def get_slug(input_text, delim=u"-"):
    result = []
    for word in _punct_re.split(input_text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word)
    return unicode(delim.join(result))
