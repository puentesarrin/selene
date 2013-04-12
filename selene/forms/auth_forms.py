# -*- coding: utf-8 *-*
from selene import constants
from selene.forms import BaseForm
from wtforms import HiddenField, TextField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(BaseForm):

    full_name = TextField(validators=[
        Required(constants.FULL_NAME_IS_REQUIRED)])
    email = TextField(validators=[Required(constants.EMAIL_IS_REQUIRED),
                                  Email(constants.EMAIL_IS_INVALID)])
    password = PasswordField(validators=[
        Required(constants.PASSWORD_IS_REQUIRED)])


class LoginForm(BaseForm):

    email = TextField(validators=[Required(constants.EMAIL_IS_REQUIRED),
                                  Email(constants.EMAIL_IS_INVALID)])
    password = PasswordField(validators=[
        Required(constants.PASSWORD_IS_REQUIRED)])
    next_ = HiddenField()


class RequestNewPasswordForm(BaseForm):

    email = TextField(validators=[Required(constants.EMAIL_IS_REQUIRED),
                                  Email(constants.EMAIL_IS_INVALID)])


class ResetPasswordForm(BaseForm):

    password = PasswordField(validators=[Required()])
