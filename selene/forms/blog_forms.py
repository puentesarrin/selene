# -*- coding: utf-8 *-*
from selene import options
from selene.forms import BaseForm
from wtforms import (TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email


class NewPostForm(BaseForm):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(NewPostForm, self).__init__(formdata, obj, prefix, **kwargs)
        self.status.choices = options.STATUSES
        self.text_type.choices = options.get_allowed_text_types()

    title = TextField(validators=[Required()])
    slug = BooleanField()
    customslug = TextField()
    tags = TextField(validators=[Required()])
    content = TextAreaField(validators=[Required()])
    status = RadioField(validators=[Required()])
    text_type = SelectField(validators=[Required()])


class NewCommentForm(BaseForm):

    name = TextField(validators=[Required()])
    email = TextField(validators=[Required(), Email()])
    content = TextAreaField(validators=[Required()])


class SearchForm(BaseForm):

    q = TextField(validators=[Required()])
