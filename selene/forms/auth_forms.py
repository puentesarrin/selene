# -*- coding: utf-8 *-*
from wtforms import Form, HiddenField, TextField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(Form):

    name = TextField(validators=[Required()])
    email = TextField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])


class LoginForm(Form):

    email = TextField(validators=[Required(), Email()])
    password = PasswordField(validators=[Required()])
    next_ = HiddenField()


class RequestNewPasswordForm(Form):

    email = TextField(validators=[Required(), Email()])


class ResetPasswordForm(Form):

    password = PasswordField(validators=[Required()])
