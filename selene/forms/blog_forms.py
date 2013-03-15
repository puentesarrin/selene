# -*- coding: utf-8 *-*
from tornado.options import options
from wtforms import (Form, TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email

_text_types = [('text', 'Text'), ('html', 'HTML'), ('rst', 'reStructuredText')]
_selected_text_types = []
_allowed_text_types = options.allowed_text_types.split(',')
for text_type in _text_types:
    if text_type[0] in _allowed_text_types:
        _selected_text_types.append(text_type)


class NewPostForm(Form):

    title = TextField(u'Title', [Required()])
    slug = BooleanField(u'Custom slug', )
    customslug = TextField()
    tags = TextField(u'Tags', [Required()])
    content = TextAreaField(u'Content', [Required()])
    status = RadioField(u'Status', [Required()],
        choices=[('published', 'Published'), ('unpublished', 'Unpublished')])

    text_type = SelectField(u'Text type', [Required()],
        choices=_selected_text_types)


class NewCommentForm(Form):

    name = TextField(u'Name', [Required()])
    email = TextField(u"E-mail", [Required(), Email()])
    content = TextAreaField(u'Content', [Required()])


class SearchForm(Form):

    q = TextField(u'Query', [Required()])
