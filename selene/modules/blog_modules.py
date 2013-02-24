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


class NewCommentModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/newcomment.html', post=post)


class CommentModule(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/comment.html", comment=comment)


class LikeComment(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/likecomment.html", comment=comment)


class DislikeComment(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/dislikecomment.html",
            comment=comment)


class DeleteComment(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/deletecomment.html",
            comment=comment)
