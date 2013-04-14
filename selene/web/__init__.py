# -*- coding: utf-8 *-*
import tornado.web

from selene.base import BaseHandler


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
