# -*- coding: utf-8 *-*
from selene.base import BaseUIModule


class LoginModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/login.html', form=form)


class GoogleLoginModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/googlelogin.html')


class TwitterLoginModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/twitterlogin.html')


class RegisterModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/register.html', form=form)


class AccountModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/account.html', form=form)


class ResetPasswordModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/resetpassword.html', form=form)


class NewPasswordModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/newpassword.html', form=form)
