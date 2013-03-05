# -*- coding: utf-8 *-*
import tornado.web

from selene.modules.auth_modules import *
from selene.modules.blog_modules import *
from selene.modules.social_modules import *


class MenuModule(tornado.web.UIModule):

    def render(self, url_path, current_user):
        return self.render_string("modules/menu.html", url_path=url_path,
            current_user=current_user)


class PoweredByModule(tornado.web.UIModule):

    def render(self):
        return self.render_string("modules/powered_by.html")
