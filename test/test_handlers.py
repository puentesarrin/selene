import tornado.testing

from selene import Selene
from test.support import FakeDB, ensure_options


class TestRegisterHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        return Selene(FakeDB())

    def test_register_url_valid(self):
        response = self.fetch('/register')
        self.assertEqual(response.code, 200)


class TestLoginHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        return Selene(FakeDB())

    def test_login_url_valid(self):
        response = self.fetch('/login')
        self.assertEqual(response.code, 200)
