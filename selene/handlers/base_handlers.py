# -*- coding: utf-8 *-*
import tornado.web

from tornado.options import options


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

    @property
    def db(self):
        return self.application.db

    @property
    def smtp(self):
        return self.application.smtp

    def get_current_user(self):
        email = self.get_secure_cookie("current_user") or False
        if not email:
            return None
        return self.db.users.find_one({"email": email})

    def get_dict_arguments(self):
        return BaseMultiDict(self)

    def get_user_locale(self):
        user = self.current_user
        if not user:
            return None
        if not user["locale"]:
            return None
        return tornado.locale.get(user["locale"])

    def render(self, template_name, **kwargs):
        posts = self.db.posts.find({'status': 'published'}).sort('date',
            -1).limit(10)
        tags = self.db.posts.aggregate([
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$limit': 20}
        ])['result']
        kwargs.update({
            'options': options,
            '_posts': posts,
            '_tags': tags
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
