# -*- coding: utf-8 *-*
import tornado.web
from tornado.options import options
from tornado.template import Template
import bcrypt
import os
import httplib


class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        user = self.get_secure_cookie("current_user") or False
        if not user:
            return None
        return tornado.escape.json_decode(user)

    def render(self, template_name, **kwargs):
        kwargs.update({'selene': self.application.config["selene"]})
        kwargs.update({'blog': self.application.config["blog"]})
        kwargs.update({'current_user': self.current_user})
        super(BaseHandler, self).render(template_name, **kwargs)


class ErrorHandler(BaseHandler):

    def __init__(self, application, request, status_code):
        BaseHandler.__init__(self, application, request)
        self.set_status(status_code)

    def write_error(self, status_code, **kwargs):
        if status_code in [403, 404, 500, 503]:
            self.require_setting("template_path")
            self.render('%d.html' % status_code)
        else:
            super(BaseHandler, self).write_error(status_code, **kwargs)

    def prepare(self):
        raise tornado.web.HTTPError(self._status_code)


class HomeHandler(BaseHandler):

    def get(self):
        self.render("home.html",
            posts=self.application.db.posts.find())


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
                "password": bcrypt.hashpw(password, bcrypt.gensalt())
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
                user = self.application.db.users.find_one({"email": email},
                    {"_id": 0})
                pass_check = bcrypt.hashpw(password,
                    user["password"]) == user["password"]
                if pass_check:
                    self.set_secure_cookie("current_user",
                        tornado.escape.json_encode(user))
                    self.redirect("/")
                else:
                    self.write("User is not exist.")
            else:
                self.write("You must fill both username and password")


class LogoutHandler(BaseHandler):

    def get(self):
        if self.current_user:
            self.clear_cookie("current_user")
        self.redirect("/")


class NewPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("postnew.html")


class PostHandler(BaseHandler):

    def get(self, slug_post):
        self.write("Post " + slug_post)


class EditPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.write("EditPost")


class DeletePostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.write("DeletePost")


class RssHandler(BaseHandler):

    def get(self):
        self.set_header("Content-Type", "text/xml; charset=UTF-8")
        self.render("rss.xml",
            posts=self.application.db.posts.find())
