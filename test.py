# -*- coding: utf-8 *-*
import tornado.locale
import unittest

from test import *

if __name__ == '__main__':
    tornado.locale.LOCALE_NAMES['zh_HK'] = {
        'name_en': 'Chinese (Hong Kong)',
        'name': '\u4e2d\u6587(\u7e41\u9ad4)'
    }
    tornado.locale.load_translations("translations")
    unittest.main()
