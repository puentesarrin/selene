# -*- coding: utf-8 *-*
import tornado.web


class NewPostModule(tornado.web.UIModule):

    def render(self, message, post, new):
        return self.render_string('modules/newpost.html', message=message,
            post=post, new=new)


class PostModule(tornado.web.UIModule):

    def render(self, post, comments, linkable=False):
        return self.render_string("modules/post.html", post=post,
            comments=comments, linkable=linkable)


class PostsPaginatorModule(tornado.web.UIModule):

    def render(self, total, page, page_size):
        return self.render_string('modules/postspaginator.html', total=total,
            page=page, page_size=page_size)


class PagerPostsModule(tornado.web.UIModule):

    def render(self, older, newer):
        return self.render_string('modules/pagerposts.html', older=older,
            newer=newer)


class PostSummaryModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/postsummary.html', post=post)


class RecentPostsModule(tornado.web.UIModule):

    def render(self, posts):
        return self.render_string("modules/recentposts.html", posts=posts)


class SearchModule(tornado.web.UIModule):

    def render(self, header=True, q=''):
        return self.render_string('modules/search.html', header=header, q=q)


class SearchPostsModule(tornado.web.UIModule):

    def render(self, title):
        return self.render_string('modules/searchposts.html', title=title)


class RecentCommentsModule(tornado.web.UIModule):

    def render(self, comments):
        return self.render_string('modules/recentcomments.html',
            comments=comments)


class TagsCloudModule(tornado.web.UIModule):

    def render(self, tags):
        return self.render_string('modules/tagscloud.html', tags=tags)


class VoteModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string("modules/vote.html", post=post)


class NewCommentModule(tornado.web.UIModule):

    def render(self, post):
        return self.render_string('modules/newcomment.html', post=post)


class CommentsModule(tornado.web.UIModule):

    def render(self, post, comments):
        return self.render_string("modules/comments.html", post=post,
            comments=comments)


class CommentModule(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/comment.html", comment=comment)


class LikeCommentModule(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/likecomment.html", comment=comment)


class DislikeCommentModule(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/dislikecomment.html",
            comment=comment)


class DeleteCommentModule(tornado.web.UIModule):

    def render(self, comment):
        return self.render_string("modules/deletecomment.html",
            comment=comment)
