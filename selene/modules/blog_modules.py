# -*- coding: utf-8 *-*
import tornado.web


class NewPostModule(tornado.web.UIModule):

    def render(self, message, post):
        return self.render_string('modules/newpost.html', message=message,
            post=post)


class PostModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/post.html", post=post)
