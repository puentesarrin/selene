# -*- coding: utf-8 *-*
import tornado.web


class Menu(tornado.web.UIModule):

    def render(self, current_user):
        return self.render_string("modules/menu.html",
            current_user=current_user)


class Post(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/post.html", post=post)


class PoweredBy(tornado.web.UIModule):

    def render(self):
        return self.render_string("modules/powered_by.html")
