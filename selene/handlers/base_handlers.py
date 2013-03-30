# -*- coding: utf-8 *-*
import functools
import tornado.escape
import tornado.gen
import tornado.web
import urllib

from motor import Op
from tornado.options import options
from selene import helpers


def authenticated_async(f):

    @functools.wraps(f)
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        self.current_user = yield tornado.gen.Task(self.get_current_user_async)
        if not self.current_user:
            self.redirect(self.get_login_url() + '?' +
                urllib.urlencode({'next': self.request.uri}))
        else:
            f(self, *args, **kwargs)
    return wrapper


def redirect_authenticated_user(f):

    @functools.wraps(f)
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        self.current_user = yield tornado.gen.Task(self.get_current_user_async)
        if self.current_user:
            self.redirect('/')
        else:
            f(self, *args, **kwargs)
    return wrapper


class BaseMultiDict(object):

    def __init__(self, handler):
        self.handler = handler

    def __iter__(self):
        return iter(self.handler.request.arguments)

    def __len__(self):
        return len(self.handler.request.arguments)

    def __contains__(self, name):
        return (name in self.handler.request.arguments)

    def getlist(self, name):
        return self.handler.get_arguments(name, strip=False)


class BaseHandler(tornado.web.RequestHandler):

    current_user = None

    @property
    def db(self):
        return self.application.db

    @property
    def smtp(self):
        return self.application.smtp

    @tornado.gen.engine
    def get_current_user_async(self, callback):
        email = self.get_secure_cookie("current_user") or False
        if not email:
            callback(None)
        else:
            callback((yield Op(self.db.users.find_one, {"email": email})))

    def get_dict_arguments(self):
        return BaseMultiDict(self)

    def get_user_locale(self):
        user = self.current_user
        if not user:
            return None
        if not user["locale"]:
            return None
        return tornado.locale.get(user["locale"])

    @tornado.gen.engine
    @tornado.web.asynchronous
    def render(self, template_name, **kwargs):
        @tornado.gen.engine
        def find_post(comment, callback):
            comment['post'] = yield Op(self.db.posts.find_one, {'_id':
                comment['postid']})
            callback(comment)

        posts = yield Op(self.db.posts.find({'status': 'published'}).sort(
            'date', -1).limit(options.recent_posts_limit).to_list)
        comments = yield Op(self.db.comments.find().sort('date', -1).limit(
            options.recent_comments_limit).to_list)
        for comment in comments:
            find_post(comment, (yield tornado.gen.Callback(comment['_id'])))
        comments = yield tornado.gen.WaitAll([comment['_id'] for comment in
            comments])
        tags = yield Op(self.db.posts.aggregate, [
            {'$match': {'status': 'published'}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$limit': options.tag_cloud_limit}
        ])
        kwargs.update({
            'current_user':
                (yield tornado.gen.Task(self.get_current_user_async)),
            'url_path': helpers.Url(self.request.uri).path,
            'options': options,
            '_next': self.get_argument('next', ''),
            '_posts': posts,
            '_comments': comments,
            '_tags': tags['result']
        })
        super(BaseHandler, self).render(template_name, **kwargs)


class ErrorHandler(BaseHandler):

    def __init__(self, application, request, status_code):
        BaseHandler.__init__(self, application, request)
        self.set_status(status_code)

    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.require_setting("template_path")
            self.render('%d.html' % status_code)
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)

    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)
