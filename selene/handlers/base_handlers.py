# -*- coding: utf-8 *-*
import tornado.web

from tornado.options import options


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

    def get_user_locale(self):
        user = self.current_user
        if not user:
            return None
        if not user["locale"]:
            return None
        return tornado.locale.get(user["locale"])

    def render(self, template_name, **kwargs):
        kwargs.update({'options': options})
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
