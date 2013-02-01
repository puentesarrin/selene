# -*- coding: utf-8 *-*
from wtforms import Form, TextField, TextAreaField
from wtforms.validators import Required


class NewPostForm(Form):

    title = TextField(u'Title', [Required()])
    custom_slug = TextField(u'Custom slug', [Required()])
    tags = TextField(u'Tags', [Required()])
    content = TextAreaField(u'Content', [Required()])
