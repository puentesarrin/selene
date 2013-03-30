# -*- coding: utf-8 *-*
import tornado.web

from tornado.options import options


class BaseUIModule(tornado.web.UIModule):

    def render_string(self, path, **kwargs):
        kwargs['options'] = options
        return super(BaseUIModule, self).render_string(path, **kwargs)
