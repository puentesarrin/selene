# -*- coding: utf-8 -*-
import pymongo
import tornado.testing

from selene import Selene


class TestPublicRoutes(tornado.testing.AsyncHTTPTestCase,
                       tornado.testing.LogTrapTestCase):

    def get_app(self):
        return Selene(pymongo.MongoClient()['selene'])

    def test_home(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)

    def test_register(self):
        response = self.fetch('/register')
        self.assertEqual(response.code, 200)

    def test_login(self):
        response = self.fetch('/login')
        self.assertEqual(response.code, 200)

    def test_feed_atom(self):
        response = self.fetch('/feed.atom')
        self.assertEqual(response.code, 200)

    def test_posts(self):
        response = self.fetch('/posts')
        self.assertEqual(response.code, 200)

    def test_tags(self):
        response = self.fetch('/tags')
        self.assertEqual(response.code, 200)

    def test_search(self):
        response = self.fetch('/search')
        self.assertEqual(response.code, 200)
