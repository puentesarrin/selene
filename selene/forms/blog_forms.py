# -*- coding: utf-8 *-*
from selene import constants, options
from selene.forms import BaseForm
from wtforms import (TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email


class PostForm(BaseForm):

    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US',
        status_choices=[], text_type_choices=[], **kwargs):
        super(PostForm, self).__init__(formdata, obj, prefix,
            locale_code=locale_code, **kwargs)
        self.status.choices = options.STATUSES
        self.text_type.choices = options.get_allowed_text_types()

    title = TextField(validators=[Required(constants.TITLE_IS_REQUIRED)])
    slug = BooleanField()
    custom_slug = TextField()
    tags = TextField(validators=[Required(constants.TAGS_ARE_REQUIRED)])
    content = TextAreaField(validators=[
        Required(constants.CONTENT_IS_REQUIRED)])
    status = RadioField(validators=[Required(constants.STATUS_IS_REQUIRED)],
        default='published')
    text_type = SelectField(validators=[
        Required(constants.TEXT_TYPE_IS_REQUIRED)])


class NewCommentForm(BaseForm):

    name = TextField(validators=[Required(constants.NAME_IS_REQUIRED)])
    email = TextField(validators=[Required(constants.EMAIL_IS_REQUIRED),
        Email(constants.EMAIL_IS_INVALID)])
    content = TextAreaField(
        validators=[Required(constants.CONTENT_IS_REQUIRED)])


class SearchForm(BaseForm):

    q = TextField(validators=[Required()])
