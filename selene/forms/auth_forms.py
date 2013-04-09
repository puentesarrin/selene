# -*- coding: utf-8 *-*
from selene.forms import BaseForm
from wtforms import HiddenField, TextField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(BaseForm):

    full_name = TextField(validators=[Required()])
    email = TextField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])


class LoginForm(BaseForm):

    email = TextField(validators=[Required('E-mail address is required'),
                                  Email('Invalid email address')])
    password = PasswordField(validators=[Required('Password is required')])
    next_ = HiddenField()


class RequestNewPasswordForm(BaseForm):

    email = TextField(validators=[Required(), Email()])


class ResetPasswordForm(BaseForm):

    password = PasswordField(validators=[Required()])
