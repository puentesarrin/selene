# -*- coding: utf-8 *-*
import tornado.web

from selene.handlers import BaseHandler
from tornado.options import options


class HomeHandler(BaseHandler):

    def get(self):
        self.render("home.html",
            posts=self.application.db.posts.find())


class NewPostHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("newpost.html")


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
            posts=self.application.db.posts.find().sort("pubdate",
                -1).limit(10),
            options=options)
