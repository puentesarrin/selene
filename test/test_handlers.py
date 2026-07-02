import tornado.testing
from tornado.options import options as opts

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

    def test_login_url_shows_social_buttons_when_enabled(self):
        opts.google_login_enabled = True
        opts.google_oauth_key = 'google-client'
        opts.google_oauth_secret = 'google-secret'
        opts.facebook_login_enabled = True
        opts.facebook_api_key = 'facebook-app'
        opts.facebook_secret = 'facebook-secret'
        opts.twitter_login_enabled = True
        opts.twitter_consumer_key = 'twitter-key'
        opts.twitter_consumer_secret = 'twitter-secret'

        response = self.fetch('/login')
        self.assertEqual(response.code, 200)
        body = response.body.decode('utf-8')
        self.assertIn('/login/google', body)
        self.assertIn('/login/facebook', body)
        self.assertIn('/login/twitter', body)

    def test_social_login_routes_return_404_when_disabled(self):
        for url in ('/login/google', '/login/facebook', '/login/twitter'):
            with self.subTest(url=url):
                response = self.fetch(url)
                self.assertEqual(response.code, 404)
