# -*- coding: utf-8 *-*
from wtforms import (Form, TextField, BooleanField, TextAreaField, RadioField,
                     SelectField)
from wtforms.validators import Required, Email


class NewPostForm(Form):

    title = TextField(u'Title', [Required()])
    slug = BooleanField(u'Custom slug', )
    customslug = TextField()
    tags = TextField(u'Tags', [Required()])
    content = TextAreaField(u'Content', [Required()])
    status = RadioField(u'Status', [Required()],
        choices=[('published', 'Published'), ('unpublished', 'Unpublished')])
    text_type = SelectField(u'Text type', [Required()],
        choices=[('text', 'Text'), ('html', 'HTML'),
                 ('rst', 'reStructuredText')])


class NewCommentForm(Form):

    name = TextField(u'Name', [Required()])
    email = TextField(u"E-mail", [Required(), Email()])
    content = TextAreaField(u'Content', [Required()])


class SearchForm(Form):

    q = TextField(u'Query', [Required()])
