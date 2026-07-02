from wtforms import HiddenField, PasswordField, SelectField, StringField
from wtforms.validators import DataRequired, Email

from selene import constants
from selene.base import BaseForm


class RegisterForm(BaseForm):
    full_name = StringField(validators=[DataRequired(constants.FULL_NAME_IS_REQUIRED)])
    email = StringField(validators=[DataRequired(constants.EMAIL_IS_REQUIRED), Email(constants.EMAIL_IS_INVALID)])
    password = PasswordField(validators=[DataRequired(constants.PASSWORD_IS_REQUIRED)])


class LoginForm(BaseForm):
    email = StringField(validators=[DataRequired(constants.EMAIL_IS_REQUIRED), Email(constants.EMAIL_IS_INVALID)])
    password = PasswordField(validators=[DataRequired(constants.PASSWORD_IS_REQUIRED)])
    next_ = HiddenField()


class RequestNewPasswordForm(BaseForm):
    email = StringField(validators=[DataRequired(constants.EMAIL_IS_REQUIRED), Email(constants.EMAIL_IS_INVALID)])


class ResetPasswordForm(BaseForm):
    password = PasswordField(validators=[DataRequired(constants.PASSWORD_IS_REQUIRED)])
    reset_hash = HiddenField()


class AccountForm(BaseForm):
    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US', language_choices=None, **kwargs):
        super().__init__(formdata, obj, prefix, locale_code=locale_code, **kwargs)
        self.language.choices = language_choices or []

    full_name = StringField(validators=[DataRequired(constants.FULL_NAME_IS_REQUIRED)])
    email = StringField(validators=[DataRequired(constants.EMAIL_IS_REQUIRED), Email(constants.EMAIL_IS_INVALID)])
    password = PasswordField()
    language = SelectField(validators=[DataRequired(constants.LANGUAGE_IS_REQUIRED)])
