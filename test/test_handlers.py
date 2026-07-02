import datetime

import tornado.testing
import tornado.web
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


class TestAdminDashboard(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        db = FakeDB()
        self.admin_user_id = ObjectId()
        self.regular_user_id = ObjectId()
        db.users.documents.extend(
            [
                {
                    '_id': self.admin_user_id,
                    'email': 'admin@example.com',
                    'full_name': 'Admin User',
                    'password': 'hashed',
                    'enabled': True,
                    'is_admin': True,
                    'locale': 'en_US',
                },
                {
                    '_id': self.regular_user_id,
                    'email': 'reader@example.com',
                    'full_name': 'Reader User',
                    'password': 'hashed',
                    'enabled': True,
                    'is_admin': False,
                    'locale': 'en_US',
                },
            ]
        )
        db.posts.documents.extend(
            [
                {
                    '_id': ObjectId(),
                    'title': 'Admin post',
                    'slug': 'admin-post',
                    'date': datetime.datetime(2026, 1, 1),
                    'tags': [],
                    'text_type': TextType.MD.value,
                    'content': 'content',
                    'html_content': '<p>content</p>',
                    'plain_content': 'content',
                    'status': PostStatus.PUBLISHED.value,
                    'author_id': self.admin_user_id,
                    'votes': 0,
                    'views': 0,
                },
                {
                    '_id': ObjectId(),
                    'title': 'Reader post',
                    'slug': 'reader-post',
                    'date': datetime.datetime(2026, 1, 2),
                    'tags': [],
                    'text_type': TextType.MD.value,
                    'content': 'content',
                    'html_content': '<p>content</p>',
                    'plain_content': 'content',
                    'status': PostStatus.UNPUBLISHED.value,
                    'author_id': self.regular_user_id,
                    'votes': 0,
                    'views': 0,
                },
            ]
        )
        db.settings.documents.append({'_id': 'site', 'title': 'Managed site', 'slogan': 'Managed slogan'})
        return Selene(db)

    def _cookie_for(self, email):
        value = tornado.web.create_signed_value(self._app.settings['cookie_secret'], 'current_user', email)
        return value.decode()

    def test_dashboard_visible_to_admin(self):
        admin_cookie = self._cookie_for('admin@example.com')
        response = self.fetch('/admin', headers={'Cookie': f'current_user={admin_cookie}'})
        self.assertEqual(response.code, 200)
        body = response.body.decode('utf-8')
        self.assertIn('Managed site', body)
        self.assertIn('Admin post', body)
        self.assertIn('Reader post', body)

    def test_dashboard_forbidden_to_regular_user(self):
        reader_cookie = self._cookie_for('reader@example.com')
        response = self.fetch('/admin', headers={'Cookie': f'current_user={reader_cookie}'}, follow_redirects=False)
        self.assertEqual(response.code, 403)


class TestPostListingPermissions(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        ensure_options()
        db = FakeDB()
        self.admin_user_id = ObjectId()
        self.regular_user_id = ObjectId()
        db.users.documents.extend(
            [
                {
                    '_id': self.admin_user_id,
                    'email': 'admin@example.com',
                    'full_name': 'Admin User',
                    'password': 'hashed',
                    'enabled': True,
                    'is_admin': True,
                    'locale': 'en_US',
                },
                {
                    '_id': self.regular_user_id,
                    'email': 'reader@example.com',
                    'full_name': 'Reader User',
                    'password': 'hashed',
                    'enabled': True,
                    'is_admin': False,
                    'locale': 'en_US',
                },
            ]
        )
        db.posts.documents.extend(
            [
                {
                    '_id': ObjectId(),
                    'title': 'Admin post',
                    'slug': 'admin-post',
                    'date': datetime.datetime(2026, 1, 1),
                    'tags': [],
                    'text_type': TextType.MD.value,
                    'content': 'content',
                    'html_content': '<p>content</p>',
                    'plain_content': 'content',
                    'status': PostStatus.PUBLISHED.value,
                    'author_id': self.admin_user_id,
                    'votes': 0,
                    'views': 0,
                },
                {
                    '_id': ObjectId(),
                    'title': 'Reader post',
                    'slug': 'reader-post',
                    'date': datetime.datetime(2026, 1, 2),
                    'tags': [],
                    'text_type': TextType.MD.value,
                    'content': 'content',
                    'html_content': '<p>content</p>',
                    'plain_content': 'content',
                    'status': PostStatus.UNPUBLISHED.value,
                    'author_id': self.regular_user_id,
                    'votes': 0,
                    'views': 0,
                },
            ]
        )
        return Selene(db)

    def _cookie_for(self, email):
        value = tornado.web.create_signed_value(self._app.settings['cookie_secret'], 'current_user', email)
        return value.decode()

    def test_regular_user_only_sees_owned_posts(self):
        reader_cookie = self._cookie_for('reader@example.com')
        response = self.fetch('/posts?title=', headers={'Cookie': f'current_user={reader_cookie}'})
        self.assertEqual(response.code, 200)
        body = response.body.decode('utf-8')
        self.assertIn('Reader post', body)
        self.assertNotIn('/post/admin-post/edit', body)
        self.assertNotIn('/post/admin-post/delete', body)
