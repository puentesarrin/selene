# -*- coding: utf-8 -*-
from selene.base import BaseHandler


class RssHandler(BaseHandler):

    def get(self):
        self.set_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.render("rss.xml",
            posts=self.db.posts.find().sort("date", -1).limit(10))