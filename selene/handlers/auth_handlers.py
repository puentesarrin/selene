# -*- coding: utf-8 *-*
import bcrypt

from selene.handlers import BaseHandler


class RegisterHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.redirect("/")
        else:
            self.render("register.html")

    def post(self):
        if self.current_user:
            self.redirect("/")
        else:
            name = self.get_argument("name", "")
            email = self.get_argument("email", "")
            password = self.get_argument("password", "")
            self.application.db.users.insert({
                "name": name,
                "email": email,
                "password": bcrypt.hashpw(password, bcrypt.gensalt()),
                "locale": self.application.default_locale["code"]
                })
            self.redirect("/login")


class LoginHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.redirect("/")
        else:
            self.render("login.html")

    def post(self):
        if self.current_user:
            self.redirect("/")
        else:
            email = self.get_argument("email", False)
            password = self.get_argument("password", False)
            if email and password:
                user = self.application.db.users.find_one({"email": email})
                pass_check = bcrypt.hashpw(password,
                    user["password"]) == user["password"]
                if pass_check:
                    self.set_secure_cookie("current_user", user["email"])
                    self.redirect("/")
                else:
                    self.write("User is not exist.")
            else:
                self.write("You must fill both username and password")


class LogoutHandler(BaseHandler):

    def post(self):
        if self.current_user:
            self.clear_cookie("current_user")
        self.redirect("/")
