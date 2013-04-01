# -*- coding: utf-8 *-*
from tornado.options import options
from wtforms import (Form, TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email

_text_types = [('text', 'Text'), ('html', 'HTML'), ('md', 'Markdown'),
    ('rst', 'reStructuredText'), ('bbcode', 'BBCode')]
_selected_text_types = []
_allowed_text_types = options.allowed_text_types.split(',')
for text_type in _text_types:
    if text_type[0] in _allowed_text_types:
        _selected_text_types.append(text_type)


class NewPostForm(Form):

    title = TextField(validators=[Required()])
    slug = BooleanField()
    customslug = TextField()
    tags = TextField(validators=[Required()])
    content = TextAreaField(validators=[Required()])
    status = RadioField(validators=[Required()],
        choices=[('published', 'Published'), ('unpublished', 'Unpublished')])

    text_type = SelectField(validators=[Required()],
        choices=_selected_text_types)


class NewCommentForm(Form):

    name = TextField(validators=[Required()])
    email = TextField(validators=[Required(), Email()])
    content = TextAreaField(validators=[Required()])


class SearchForm(Form):

    q = TextField(validators=[Required()])
