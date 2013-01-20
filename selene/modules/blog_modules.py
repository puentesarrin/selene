# -*- coding: utf-8 *-*
import tornado.web


class NewPostModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/newpost.html')


class PostModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/post.html", post=post)
