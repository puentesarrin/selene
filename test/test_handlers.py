# -*- coding: utf-8 *-*
import pymongo
import tornado.testing

from selene import Selene, options


class TestRegisterHandler(tornado.testing.AsyncHTTPTestCase,
                          tornado.testing.LogTrapTestCase):

    def get_app(self):
        options.setup_options('selene.conf')
        return Selene(pymongo.MongoClient()['selene'])

    def test_register_url_valid(self):
        response = self.fetch('/register')
        self.assertEqual(response.code, 200)

        response = self.fetch('/register/')
        self.assertEqual(response.code, 200)
