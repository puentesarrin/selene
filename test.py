# -*- coding: utf-8 *-*
import unittest

from selene import options
from test import *

if __name__ == '__main__':
    options.setup_options('selene.conf')
    unittest.main()
