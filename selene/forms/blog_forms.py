# -*- coding: utf-8 *-*
from wtforms import Form, TextField, BooleanField, TextAreaField, RadioField
from wtforms.validators import Required


class NewPostForm(Form):

    title = TextField(u'Title', [Required()])
    slug = BooleanField(u'Custom slug', )
    customslug = TextField()
    tags = TextField(u'Tags', [Required()])
    content = TextAreaField(u'Content', [Required()])
    status = RadioField(u'Status', [Required()],
        choices=[('published', 'Published'), ('unpublished', 'Unpublished')])
