from __future__ import annotations

import functools
from urllib.parse import urlencode

import tornado.escape
import tornado.locale
import tornado.web
from typing import TYPE_CHECKING, Any, Protocol, cast
from tornado.options import options

from selene import forms, helpers
from selene import options as opts
from selene.constants import PostStatus
from selene.smtp import SMTP

if TYPE_CHECKING:
    from pymongo.asynchronous.database import AsyncDatabase


class _AppWithDbAndSmtp(Protocol):
    db: AsyncDatabase[Any]
    smtp: SMTP


def authenticated_async(f):

    @functools.wraps(f)
    async def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.redirect(self.get_login_url() + '?' + urlencode({'next': self.request.uri}))
            return
        return await f(self, *args, **kwargs)

    return wrapper


def redirect_authenticated_user(f):

    @functools.wraps(f)
    async def wrapper(self, *args, **kwargs):
        if self.current_user:
            self.redirect(self.reverse_url('home'))
            return
        return await f(self, *args, **kwargs)

    return wrapper


def validate_form(form_class, template, **params):

    def decorator(f):

        @functools.wraps(f)
        async def wrapper(self, *args, **kwargs):
            self.form = form_class(self.request.arguments, locale_code=self.locale.code, **params)
            if not self.form.validate():
                await self.render(template, message=self.form.errors, form=self.form)
                return
            return await f(self, *args, **kwargs)

        return wrapper

    return decorator


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self) -> AsyncDatabase[Any]:
        return cast(_AppWithDbAndSmtp, self.application).db

    @property
    def smtp(self) -> SMTP:
        return cast(_AppWithDbAndSmtp, self.application).smtp

    async def prepare(self):
        self._current_user = await self.get_current_user_async()
        self._user_cache: dict[Any, dict[str, Any] | None] = {}

    def get_current_user(self):
        return getattr(self, '_current_user', None)

    async def get_current_user_async(self):
        email = self.get_secure_cookie('current_user')
        if not email:
            return None
        email = tornado.escape.to_unicode(email)
        return await self.db.users.find_one({'email': email})

    def get_user_locale(self):
        user = self.current_user
        if not user:
            locale_cookie = self.get_cookie('locale')
            if locale_cookie in [code for code, _ in opts.get_allowed_languages()]:
                return tornado.locale.get(locale_cookie)
            return None
        if not user.get('locale'):
            return None
        return tornado.locale.get(user['locale'])

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace.update(
            {
                'arguments': self.request.arguments,
                'forms': forms,
                'helpers': helpers,
                'options': options,
                'opts': opts,
                'language_choices': opts.get_allowed_languages(),
            }
        )
        return namespace

    @staticmethod
    def _user_name(user: dict[str, Any]) -> str:
        return str(user.get('full_name') or user.get('name') or user.get('email') or '')

    async def _user_by_id(self, user_id: Any) -> dict[str, Any] | None:
        if not user_id:
            return None
        user_cache = getattr(self, '_user_cache', None)
        if user_cache is None:
            user_cache = self._user_cache = {}
        if user_id not in user_cache:
            user_cache[user_id] = await self.db.users.find_one({'_id': user_id})
        return user_cache[user_id]

    async def hydrate_post(self, post: dict[str, Any]) -> dict[str, Any]:
        user = await self._user_by_id(post.get('author_id'))
        if user:
            post['author'] = self._user_name(user)
            post['email'] = user.get('email')
        if post.get('comments'):
            await self.hydrate_comments(post['comments'])
        return post

    async def hydrate_posts(self, posts: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for post in posts:
            await self.hydrate_post(post)
        return posts

    async def hydrate_comment(self, comment: dict[str, Any]) -> dict[str, Any]:
        user = await self._user_by_id(comment.get('author_id'))
        if user:
            comment['name'] = self._user_name(user)
            comment['email'] = user.get('email')
        if comment.get('post'):
            await self.hydrate_post(comment['post'])
        return comment

    async def hydrate_comments(self, comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for comment in comments:
            await self.hydrate_comment(comment)
        return comments

    async def render(self, template_name, **kwargs):
        posts = (
            await self.db.posts.find({'status': PostStatus.PUBLISHED.value})
            .sort('date', -1)
            .limit(options.recent_posts_limit)
            .to_list(None)
        )
        comments = await self.db.comments.find().sort('date', -1).limit(options.recent_comments_limit).to_list(None)
        for comment in comments:
            comment['post'] = await self.db.posts.find_one({'_id': comment['postid']})
        await self.hydrate_posts(posts)
        await self.hydrate_comments(comments)
        tags_cursor = await self.db.posts.aggregate(
            [
                {'$match': {'status': PostStatus.PUBLISHED.value}},
                {'$unwind': '$tags'},
                {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
                {'$limit': options.tag_cloud_limit},
            ]
        )
        tags = await tags_cursor.to_list(None)
        for key in ('post', 'comment'):
            value = kwargs.get(key)
            if isinstance(value, dict):
                if key == 'post':
                    await self.hydrate_post(value)
                else:
                    await self.hydrate_comment(value)
        for key in ('posts', '_posts'):
            value = kwargs.get(key)
            if isinstance(value, list):
                await self.hydrate_posts(value)
        for key in ('comments', '_comments'):
            value = kwargs.get(key)
            if isinstance(value, list):
                await self.hydrate_comments(value)
        kwargs.update(
            {
                'current_user': self.current_user,
                'url_path': self.request.uri,
                '_next': self.get_argument('next', ''),
                '_posts': posts,
                '_comments': comments,
                'opts': opts,
                'options': options,
                'forms': forms,
                '_tags': tags,
            }
        )
        super().render(template_name, **kwargs)


class ErrorHandler(BaseHandler):
    def __init__(self, application, request, status_code):
        super().__init__(application, request)
        self.set_status(status_code)

    async def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.require_setting('template_path')
            await self.render(f'{status_code}.html')
        else:
            super().write_error(status_code, **kwargs)

    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)
