# -*- coding: utf-8 *-*
import bcrypt

from selene.handlers import BaseHandler
from tornado.options import options


class AuthBaseHandler(BaseHandler):

    def prepare(self):
        if self.current_user:
            self.redirect("/")


class RegisterHandler(AuthBaseHandler):

    def get(self):
        self.render("register.html")

    def post(self):
        name = self.get_argument("name", "")
        email = self.get_argument("email", "")
        password = self.get_argument("password", "")
        if self.db.users.find_one({'email': email}):
            self.render('login.html', message='e-mail address already '
                'registered')
            return
        self.db.users.insert({
            "name": name,
            "email": email,
            "password": bcrypt.hashpw(password, bcrypt.gensalt()),
            "locale": options.default_language
            })
        self.redirect("/login")


class LoginHandler(AuthBaseHandler):

    def get(self):
        self.render("login.html", message='')

    def post(self):
        email = self.get_argument("email", False)
        password = self.get_argument("password", False)
        if email and password:
            user = self.db.users.find_one({"email": email})
            if user:
                pass_check = bcrypt.hashpw(password,
                    user["password"]) == user["password"]
                if pass_check:
                    self.set_secure_cookie("current_user", user["email"])
                    self.redirect("/")
                    return
        self.render('login.html',
            message="Incorrect user/password combination")


class LogoutHandler(BaseHandler):

    def post(self):
        if not self.current_user:
            self.redirect('/')
            return
        self.clear_cookie("current_user")
        self.redirect("/")
