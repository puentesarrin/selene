# -*- coding: utf-8 *-*


def remove_duplicates(l, separator=','):
    if isinstance(l, basestring):
        l = l.split(separator)
    return list(set(l))
