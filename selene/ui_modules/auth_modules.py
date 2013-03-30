# -*- coding: utf-8 *-*
from selene.web import BaseUIModule


class LoginModule(BaseUIModule):

    def render(self, _next):
        return self.render_string('modules/login.html', _next=_next)


class GoogleLoginModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/googlelogin.html')


class TwitterLoginModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/twitterlogin.html')


class RegisterModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/register.html')


class ResetPasswordModule(BaseUIModule):

    def render(self, reset_hash):
        return self.render_string('modules/resetpassword.html',
            reset_hash=reset_hash)


class NewPasswordModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/newpassword.html')
