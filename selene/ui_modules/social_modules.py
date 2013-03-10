# -*- coding: utf-8 *-*
import tornado.web


class TwitterShareModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/twittershare.html', post=post)


class FacebookShareModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/facebookshare.html', post=post)


class GooglePlusShareModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/googleplusshare.html', post=post)


class DisqusModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/disqus.html')
