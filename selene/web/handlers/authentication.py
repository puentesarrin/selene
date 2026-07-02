import datetime

import bcrypt
import tornado.web
from pymongo import ReturnDocument
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


class LoginGoogleHandler(BaseHandler):
    async def get(self):
        raise tornado.web.HTTPError(410)


class LoginTwitterHandler(BaseHandler):
    async def get(self):
        raise tornado.web.HTTPError(410)


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
