# -*- coding: utf-8 *-*
from selene import options
from wtforms import (Form, TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email


class NewPostForm(Form):

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


class NewCommentForm(Form):

    name = TextField(validators=[Required()])
    email = TextField(validators=[Required(), Email()])
    content = TextAreaField(validators=[Required()])


class SearchForm(Form):

    q = TextField(validators=[Required()])
