# -*- coding: utf-8 *-*
from selene.base import BaseUIModule
from selene.web.ui_modules.auth_modules import *
from selene.web.ui_modules.blog_modules import *
from selene.web.ui_modules.social_modules import *


class MenuModule(BaseUIModule):

    def render(self, url_path, current_user):
        return self.render_string("modules/menu.html", url_path=url_path,
            current_user=current_user)


class MessageModule(BaseUIModule):

    def render(self, message):
        return self.render_string('modules/message.html', message=message)


class PoweredByModule(BaseUIModule):

    def render(self):
        return self.render_string("modules/powered_by.html")


class GoogleAnalyticsModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/googleanalytics.html')
