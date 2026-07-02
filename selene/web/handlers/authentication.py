import datetime
from typing import Any
from urllib.parse import urljoin

import bcrypt
import tornado.auth
import tornado.web
from pymongo import ReturnDocument
from tornado.escape import to_unicode
from tornado.options import options

import selene.web
from selene import constants, forms, helpers
from selene import options as opts
from selene.web import BaseHandler


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def _profile_id(profile: dict[str, Any]) -> str:
    provider_id = profile.get('id') or profile.get('username') or profile.get('screen_name')
    if not provider_id:
        raise tornado.web.HTTPError(503, 'The third-party provider did not return a user identifier.')
    return str(provider_id)


def _profile_email(provider: str, provider_id: str, profile: dict[str, Any]) -> str:
    email = profile.get('email')
    if email:
        return str(email)
    return f'{provider}-{provider_id}@selene.local'


def _profile_name(provider: str, provider_id: str, profile: dict[str, Any], email: str) -> str:
    name = profile.get('name') or profile.get('full_name')
    if name:
        return str(name)
    first_name = profile.get('first_name')
    last_name = profile.get('last_name')
    if first_name or last_name:
        return ' '.join(part for part in [first_name, last_name] if part)
    if provider == 'twitter':
        username = profile.get('username') or profile.get('screen_name')
        if username:
            return str(username)
    if provider == 'google' and profile.get('given_name'):
        return str(profile['given_name'])
    return email.split('@', 1)[0] or provider_id


class RegisterHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def get(self):
        await self.render('register.html', form=forms.RegisterForm(locale_code=self.locale.code))

    @selene.web.redirect_authenticated_user
    @selene.web.validate_form(forms.RegisterForm, 'register.html')
    async def post(self):
        existing = await self.db.users.find_one({'email': self.form.data['email']}, {'_id': 1})
        if existing:
            return await self.render('register.html', message=constants.EMAIL_IS_ALREADY_REGISTERED, form=self.form)

        user = dict(self.form.data)
        user.update(
            {
                'password': hash_password(self.form.data['password']),
                'enabled': False,
                'is_admin': False,
                'join': datetime.datetime.now(),
                'join_hash': helpers.generate_md5(),
                'locale': options.default_language,
            }
        )
        await self.db.users.insert_one(user)
        await self.smtp.send(constants.CONFIRM_YOUR_ACCOUNT, 'newuser.html', user['email'], {'user': user})
        self.redirect(self.reverse_url('login'))


class ConfirmAccountHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def get(self, join_hash=None):
        await self.db.users.find_one_and_update(
            {'join_hash': join_hash}, {'$unset': {'join_hash': 1}, '$set': {'enabled': True}}
        )
        await self.render('confirmaccount.html')


class LoginHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def get(self):
        await self.render(
            'login.html', form=forms.LoginForm(locale_code=self.locale.code, next_=self.get_argument('next', '/'))
        )

    @selene.web.redirect_authenticated_user
    @selene.web.validate_form(forms.LoginForm, 'login.html')
    async def post(self):
        user = await self.db.users.find_one({'email': self.form.data['email']})
        if user and user.get('enabled') and check_password(self.form.data['password'], user['password']):
            self.set_secure_cookie('current_user', user['email'])
            self.redirect(self.form.data['next_'] or self.reverse_url('home'))
            return
        await self.render('login.html', message=constants.INCORRECT_USER_PASSWORD, form=self.form)


class _ThirdPartyLoginHandler(BaseHandler):
    provider_name = ''
    login_route = ''

    def _enabled(self) -> bool:
        return False

    def _callback_uri(self) -> str:
        return urljoin(opts.base_url.rstrip('/') + '/', self.reverse_url(self.login_route).lstrip('/'))

    def _remember_next(self) -> None:
        self.set_secure_cookie('login_next', self.get_argument('next', self.reverse_url('home')))

    def _consume_next(self) -> str:
        next_url = self.get_secure_cookie('login_next')
        self.clear_cookie('login_next')
        if next_url:
            return to_unicode(next_url)
        return self.reverse_url('home')

    async def _finish_login(self, profile: dict[str, Any]) -> None:
        provider_id = _profile_id(profile)
        email = _profile_email(self.provider_name, provider_id, profile)
        full_name = _profile_name(self.provider_name, provider_id, profile, email)
        user = await self.db.users.find_one(
            {'$or': [{'auth_provider': self.provider_name, 'auth_id': provider_id}, {'email': email}]}
        )
        update = {
            'email': email,
            'full_name': full_name,
            'enabled': True,
            'is_admin': False,
            'locale': options.default_language,
            'auth_provider': self.provider_name,
            'auth_id': provider_id,
        }
        if user:
            user = await self.db.users.find_one_and_update(
                {'_id': user['_id']}, {'$set': update}, return_document=ReturnDocument.AFTER
            )
        else:
            user = dict(update)
            user['join'] = datetime.datetime.now()
            user['password'] = ''
            result = await self.db.users.insert_one(user)
            user['_id'] = result.inserted_id

        self.set_secure_cookie('current_user', user['email'])
        self.redirect(self._consume_next())


class LoginGoogleHandler(tornado.auth.GoogleOAuth2Mixin, _ThirdPartyLoginHandler):
    provider_name = 'google'
    login_route = 'login-google'

    def _enabled(self) -> bool:
        return bool(options.google_login_enabled and self.settings.get('google_oauth'))

    async def get(self):
        if not self._enabled():
            raise tornado.web.HTTPError(404)
        callback_uri = self._callback_uri()
        if self.get_argument('code', False):
            access = await self.get_authenticated_user(redirect_uri=callback_uri, code=self.get_argument('code'))
            user = await self.oauth2_request(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                access_token=access['access_token'],
            )
            await self._finish_login(user)
            return

        self._remember_next()
        self.authorize_redirect(
            redirect_uri=callback_uri,
            client_id=self.get_google_oauth_settings()['key'],
            scope=['profile', 'email'],
            response_type='code',
            extra_params={'prompt': 'select_account'},
        )


class LoginFacebookHandler(tornado.auth.FacebookGraphMixin, _ThirdPartyLoginHandler):
    provider_name = 'facebook'
    login_route = 'login-facebook'

    def _enabled(self) -> bool:
        return bool(
            options.facebook_login_enabled
            and self.settings.get('facebook_api_key')
            and self.settings.get('facebook_secret')
        )

    async def get(self):
        if not self._enabled():
            raise tornado.web.HTTPError(404)
        callback_uri = self._callback_uri()
        if self.get_argument('code', False):
            user = await self.get_authenticated_user(
                redirect_uri=callback_uri,
                client_id=self.settings['facebook_api_key'],
                client_secret=self.settings['facebook_secret'],
                code=self.get_argument('code'),
                extra_fields={'email'},
            )
            if not user:
                raise tornado.web.HTTPError(503)
            await self._finish_login(user)
            return

        self._remember_next()
        self.authorize_redirect(
            redirect_uri=callback_uri,
            client_id=self.settings['facebook_api_key'],
            scope=['email'],
        )


class LoginTwitterHandler(tornado.auth.TwitterMixin, _ThirdPartyLoginHandler):
    provider_name = 'twitter'
    login_route = 'login-twitter'

    def _enabled(self) -> bool:
        return bool(
            options.twitter_login_enabled
            and self.settings.get('twitter_consumer_key')
            and self.settings.get('twitter_consumer_secret')
        )

    async def get(self):
        if not self._enabled():
            raise tornado.web.HTTPError(404)
        callback_uri = self._callback_uri()
        if self.get_argument('oauth_token', False):
            user = await self.get_authenticated_user()
            await self._finish_login(user)
            return

        self._remember_next()
        await self.authenticate_redirect(callback_uri=callback_uri)


class AccountHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        form = forms.AccountForm(
            locale_code=self.locale.code,
            language_choices=opts.get_allowed_languages(),
            language=self.get_user_locale().code,
            **self.current_user,
        )
        await self.render('account.html', form=form)

    @tornado.web.authenticated
    async def post(self):
        form = forms.AccountForm(
            self.request.arguments, locale_code=self.locale.code, language_choices=opts.get_allowed_languages()
        )
        form.email.process_data(self.current_user['email'])
        if form.validate():
            update = {'$set': {'full_name': form.data['full_name'], 'locale': form.data['language']}}
            if form.data['password']:
                update['$set'].update({'password': hash_password(form.data['password'])})
            await self.db.users.update_one({'email': self.current_user['email']}, update)
            self.redirect(self.reverse_url('my-account'))
        else:
            await self.render('account.html', message=form.errors, form=form)


class ChangeLanguageHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def post(self):
        form = forms.LanguageForm(self.request.arguments)
        self.set_cookie('locale', form.data['language'])
        self.redirect(self.reverse_url('home'))


class RequestNewPasswordHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def get(self):
        await self.render('newpassword.html', form=forms.RequestNewPasswordForm(locale_code=self.locale.code))

    @selene.web.redirect_authenticated_user
    @selene.web.validate_form(forms.RequestNewPasswordForm, 'newpassword.html')
    async def post(self):
        user = await self.db.users.find_one({'email': self.form.data['email']})
        if user:
            reset_hash = helpers.generate_md5()
            user = await self.db.users.find_one_and_update(
                {'email': self.form.data['email']},
                {'$set': {'reset_hash': reset_hash, 'enabled': True}, '$unset': {'join_hash': 1}},
                return_document=ReturnDocument.AFTER,
            )
            await self.smtp.send(constants.RESET_PASSWORD, 'newpassword.html', user['email'], {'user': user})
            self.redirect(self.reverse_url('home'))
            return
        await self.render('newpassword.html', message=constants.USER_IS_NOT_EXIST, form=self.form)


class ResetPasswordHandler(BaseHandler):
    @selene.web.redirect_authenticated_user
    async def get(self, reset_hash=''):
        await self.render('resetpassword.html', form=forms.ResetPasswordForm(reset_hash=reset_hash))

    @selene.web.redirect_authenticated_user
    async def post(self, reset_hash=None):
        form = forms.ResetPasswordForm(self.request.arguments, locale_code=self.locale.code, reset_hash=reset_hash)
        if form.validate():
            password = hash_password(form.data['password'])
            user = await self.db.users.find_one_and_update(
                {'reset_hash': reset_hash}, {'$set': {'password': password}}, return_document=ReturnDocument.AFTER
            )
            if user:
                await self.smtp.send(constants.UPDATED_PASSWORD, 'resetpassword.html', user['email'], {'user': user})
            self.redirect(self.reverse_url('login'))
        else:
            await self.render('resetpassword.html', message=form.errors, form=form)


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    async def post(self):
        self.clear_cookie('current_user')
        self.redirect(self.reverse_url('home'))
