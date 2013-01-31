# -*- coding: utf-8 *-*
from wtforms import Form, TextField, PasswordField
from wtforms.validators import Required, Email


class RegisterForm(Form):

    name = TextField(u"Full name", [Required()])
    email = TextField(u"E-mail", [Required(), Email()])
    password = PasswordField(u"Password", [Required()])


class LoginForm(Form):

    email = TextField(u"E-mail", [Required(), Email()])
    password = PasswordField(u"Password", [Required()])
