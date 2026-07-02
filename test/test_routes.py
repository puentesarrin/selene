import tornado.testing

from selene import Selene
from test.support import FakeDB, ensure_options


class TestPublicRoutes(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        return Selene(FakeDB())

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

    def test_posts_redirects_to_login(self):
        response = self.fetch('/posts', follow_redirects=False)
        self.assertEqual(response.code, 302)

    def test_tags(self):
        response = self.fetch('/tags')
        self.assertEqual(response.code, 200)

    def test_search(self):
        response = self.fetch('/search')
        self.assertEqual(response.code, 200)
