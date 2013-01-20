# -*- coding: utf-8 *-*
import tornado.web


class MenuModule(tornado.web.UIModule):

    def render(self, current_user):
        return self.render_string("modules/menu.html",
            current_user=current_user)


class LoginModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/login.html')


class RegisterModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/register.html')


class ResetPasswordModule(tornado.web.UIModule):

    def render(self, reset_hash):
        return self.render_string('modules/resetpassword.html',
            reset_hash=reset_hash)


class NewPasswordModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/newpassword.html')


class NewPostModule(tornado.web.UIModule):

    def render(self):
        return self.render_string('modules/newpost.html')


class PostModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/post.html", post=post)


class PoweredByModule(tornado.web.UIModule):

    def render(self):
        return self.render_string("modules/powered_by.html")
