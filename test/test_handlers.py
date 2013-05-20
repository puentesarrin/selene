# -*- coding: utf-8 *-*
import pymongo
import tornado.testing

from selene import Selene


class TestRegisterHandler(tornado.testing.AsyncHTTPTestCase,
                          tornado.testing.LogTrapTestCase):

    def get_app(self):
        return Selene(pymongo.MongoClient()['selene'])

    def test_register_url_valid(self):
        response = self.fetch('/register')
        self.assertEqual(response.code, 200)


class TestLoginHandler(tornado.testing.AsyncHTTPTestCase,
                       tornado.testing.LogTrapTestCase):

    def get_app(self):
        return Selene(pymongo.MongoClient()['selene'])

    def test_login_url_valid(self):
        response = self.fetch('/login')
        self.assertEqual(response.code, 200)
