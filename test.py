# -*- coding: utf-8 *-*
import tornado.locale
import unittest

from test import *

if __name__ == '__main__':
    tornado.locale.LOCALE_NAMES['zh_HK'] = {
        'name_en': 'Chinese (Hong Kong)',
        'name': ''
    }
    tornado.locale.load_translations("translations")
    unittest.main()
