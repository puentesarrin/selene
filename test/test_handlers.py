import datetime

import tornado.testing
from bson.objectid import ObjectId
from tornado.options import options as opts

from selene import Selene, helpers
from selene.constants import PostStatus, TextType
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



class TestPostHydration(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        db = FakeDB()
        user_id = ObjectId()
        post_id = ObjectId()
        db.users.documents.append(
            {
                '_id': user_id,
                'email': 'updated@example.com',
                'full_name': 'Updated Name',
                'locale': 'en_US',
            }
        )
        db.posts.documents.append(
            {
                '_id': post_id,
                'title': 'Hydrated post',
                'slug': 'hydrated-post',
                'date': datetime.datetime(2026, 1, 1),
                'tags': [],
                'text_type': TextType.MD.value,
                'content': 'content',
                'html_content': '<p>content</p>',
                'plain_content': 'content',
                'status': PostStatus.PUBLISHED.value,
                'author_id': user_id,
                'author': 'Stale Name',
                'email': 'stale@example.com',
                'votes': 0,
                'views': 0,
            }
        )
        db.comments.documents.append(
            {
                '_id': ObjectId(),
                'postid': post_id,
                'author_id': user_id,
                'name': 'Old Comment Name',
                'email': 'old-comment@example.com',
                'content': 'A comment',
                'date': datetime.datetime(2026, 1, 2),
                'likes': 0,
                'dislikes': 0,
            }
        )
        return Selene(db)

    def test_post_page_hydrates_author_and_comment_from_user(self):
        opts.gravatar_for_posts = True
        opts.gravatar_for_comments = True
        response = self.fetch('/post/hydrated-post')
        self.assertEqual(response.code, 200)
        body = response.body.decode('utf-8')
        self.assertIn('Updated Name', body)
        self.assertIn(helpers.get_gravatar_url('updated@example.com', 70), body)
        self.assertIn(helpers.get_gravatar_url('updated@example.com', 48), body)
        self.assertNotIn('Stale Name', body)
        self.assertNotIn('Old Comment Name', body)
