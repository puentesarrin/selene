# -*- coding: utf-8 *-*
import tornado.web


class LoginModule(tornado.web.UIModule):

    def render(self, next_):
        return self.render_string('modules/login.html', next_=next_)


class RegisterModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/register.html')


class ResetPasswordModule(tornado.web.UIModule):

    def render(self, reset_hash):
        return self.render_string('modules/resetpassword.html',
            reset_hash=reset_hash)


class NewPasswordModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/newpassword.html')
