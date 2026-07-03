from wtforms import BooleanField, RadioField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Email

from selene import constants
from wtforms_tornado import BaseForm
from selene.constants import PostStatus


class PostForm(BaseForm):
    def __init__(
        self,
        formdata=None,
        obj=None,
        prefix='',
        locale_code='en_US',
        status_choices=None,
        text_type_choices=None,
        **kwargs,
    ):
        super().__init__(formdata, obj, prefix, locale_code=locale_code, **kwargs)
        self.status.choices = status_choices or []
        self.text_type.choices = text_type_choices or []

    title = StringField(validators=[DataRequired(constants.TITLE_IS_REQUIRED)])
    custom_slug = BooleanField()
    slug = StringField()
    tags = StringField(validators=[DataRequired(constants.TAGS_ARE_REQUIRED)])
    content = TextAreaField(validators=[DataRequired(constants.CONTENT_IS_REQUIRED)])
    status = RadioField(validators=[DataRequired(constants.STATUS_IS_REQUIRED)], default=PostStatus.PUBLISHED.value)
    text_type = SelectField(validators=[DataRequired(constants.TEXT_TYPE_IS_REQUIRED)])


class CommentForm(BaseForm):
    name = StringField(validators=[DataRequired(constants.NAME_IS_REQUIRED)])
    email = StringField(validators=[DataRequired(constants.EMAIL_IS_REQUIRED), Email(constants.EMAIL_IS_INVALID)])
    content = TextAreaField(validators=[DataRequired(constants.CONTENT_IS_REQUIRED)])


class LanguageForm(BaseForm):
    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US', language_choices=None, **kwargs):
        super().__init__(formdata, obj, prefix, locale_code=locale_code, **kwargs)
        self.language.choices = language_choices or []

    language = SelectField(validators=[DataRequired(constants.LANGUAGE_IS_REQUIRED)])


class SearchForm(BaseForm):
    q = StringField(validators=[DataRequired()])
