# -*- coding: utf-8 *-*
from selene.web import BaseUIModule


class TwitterShareModule(BaseUIModule):

    def render(self, post):
        return self.render_string('modules/twittershare.html', post=post)


class FacebookShareModule(BaseUIModule):

    def render(self, post):
        return self.render_string('modules/facebookshare.html', post=post)


class GooglePlusShareModule(BaseUIModule):

    def render(self, post):
        return self.render_string('modules/googleplusshare.html', post=post)


class DisqusModule(BaseUIModule):

    def render(self):
        return self.render_string('modules/disqus.html')
