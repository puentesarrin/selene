# -*- coding: utf-8 *-*
import tornado.web


class NewPostModule(tornado.web.UIModule):

    def render(self, message, post, new):
        return self.render_string('modules/newpost.html', message=message,
            post=post, new=new)


class PostModule(tornado.web.UIModule):

    def render(self, post, linkable=False):
        return self.render_string("modules/post.html", post=post,
            linkable=linkable)


class VoteModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/vote.html", post=post)
