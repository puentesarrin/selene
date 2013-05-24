# -*- coding: utf-8 *-*
import functools
import tornado.web

from selene.base import BaseHandler


def redirect_authenticated_user(f):

    @functools.wraps(f)
    @tornado.gen.engine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        if self.current_user:
            self.redirect(self.reverse_url('home'))
        else:
            f(self, *args, **kwargs)
    return wrapper


def validate_form(form_class, template):

    def decorator(f):

        @functools.wraps(f)
        @tornado.gen.engine
        def wrapper(self, *args, **kwargs):
            self.form = form_class(self.request.arguments)
            if not self.form.validate():
                self.render(template, message=self.form.errors, form=self.form)
            else:
                f(self, *args, **kwargs)
        return wrapper
    return decorator


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
