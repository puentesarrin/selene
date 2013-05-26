# -*- coding: utf-8 -*-
import selene

from selene.base import BaseHandler
from tornado.options import options
from werkzeug.contrib.atom import AtomFeed


class RSSHandler(BaseHandler):

    def get(self):
        self.set_header("Content-Type", "application/rss+xml; charset=utf-8")
        self.render("rss.xml",
            posts=self.db.posts.find().sort("date", -1).limit(10))


class AtomHandler(BaseHandler):

    def get(self):
        generator = ('Selene', 'https://github.com/puentesarrin/selene',
                     selene.version)
        feed = AtomFeed(title=options.title, feed_url=self.reverse_url('atom'),
                        url=options.base_url, generator=generator)
        posts = self.db.posts.find().sort("date", -1).limit(10)
        for post in posts:
            feed.add(title=post['title'], content=post['html_content'],
                     content_type='html', author=post['author'],
                     url=self.reverse_url('post', post['slug']),
                     published=post['date'], updated=post['date'])
        self.set_header('Content-Type', 'application/atom+xml; charset=UTF-8')
        self.write(str(feed))
        self.finish()