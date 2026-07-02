from urllib.parse import urlencode

import tornado.web

from tornado.options import options
from selene.base import BaseUIModule


def _login_url(handler, route_name):
    url = handler.reverse_url(route_name)
    next_ = handler.get_argument('next', '')
    if next_:
        url = f'{url}?{urlencode({"next": next_})}'
    return url


class LoginModule(BaseUIModule):
    def render(self, form):
        return self.render_string(
            'modules/login.html',
            form=form,
        )


class GoogleLoginModule(BaseUIModule):
    def render(self):
        if not (options.google_login_enabled and options.google_oauth_key and options.google_oauth_secret):
            raise tornado.web.HTTPError(404)
        return self.render_string('modules/googlelogin.html', login_url=_login_url(self.handler, 'login-google'))


class FacebookLoginModule(BaseUIModule):
    def render(self):
        if not (options.facebook_login_enabled and options.facebook_api_key and options.facebook_secret):
            raise tornado.web.HTTPError(404)
        return self.render_string('modules/facebooklogin.html', login_url=_login_url(self.handler, 'login-facebook'))


class TwitterLoginModule(BaseUIModule):
    def render(self):
        if not (
            options.twitter_login_enabled and options.twitter_consumer_key and options.twitter_consumer_secret
        ):
            raise tornado.web.HTTPError(404)
        return self.render_string('modules/twitterlogin.html', login_url=_login_url(self.handler, 'login-twitter'))


class RegisterModule(BaseUIModule):
    def render(self, form):
        return self.render_string(
            'modules/register.html',
            form=form,
        )


class AccountModule(BaseUIModule):
    def render(self, form):
        return self.render_string(
            'modules/account.html',
            form=form,
        )


class ResetPasswordModule(BaseUIModule):
    def render(self, form):
        return self.render_string(
            'modules/resetpassword.html',
            form=form,
        )


class NewPasswordModule(BaseUIModule):
    def render(self, form):
        return self.render_string(
            'modules/newpassword.html',
            form=form,
        )
