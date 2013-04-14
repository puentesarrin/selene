# -*- coding: utf-8 *-*
from selene.web import BaseUIModule


class NewPostModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/newpost.html', form=form)


class EditPostModule(BaseUIModule):

    def render(self, form):
        return self.render_string('modules/editpost.html', form=form)


class PostModule(BaseUIModule):

    def render(self, post, comments, linkable=False):
        return self.render_string("modules/post.html", post=post,
            comments=comments, linkable=linkable)


class PostsPaginatorModule(BaseUIModule):

    def render(self, total, page, page_size):
        return self.render_string('modules/postspaginator.html', total=total,
            page=page, page_size=page_size)


class TagPostsPaginatorModule(BaseUIModule):

    def render(self, tag, total, page, page_size):
        return self.render_string('modules/tagpostspaginator.html', tag=tag,
            total=total, page=page, page_size=page_size)


class SearchPostsPaginatorModule(BaseUIModule):

    def render(self, q, total, page, page_size):
        return self.render_string('modules/searchpostspaginator.html', q=q,
            total=total, page=page, page_size=page_size)


class OlderNewerPostsModule(BaseUIModule):

    def render(self, older, newer):
        return self.render_string('modules/oldernewerposts.html', older=older,
            newer=newer)


class PostSummaryModule(BaseUIModule):

    def render(self, post):
        return self.render_string('modules/postsummary.html', post=post)


class RecentPostsModule(BaseUIModule):

    def render(self, posts):
        return self.render_string("modules/recentposts.html", posts=posts)


class SearchModule(BaseUIModule):

    def render(self, form, header=True):
        return self.render_string('modules/search.html', header=header,
            form=form)


class SearchPostsModule(BaseUIModule):

    def render(self, title):
        return self.render_string('modules/searchposts.html', title=title)


class RecentCommentsModule(BaseUIModule):

    def render(self, comments):
        return self.render_string('modules/recentcomments.html',
            comments=comments)


class TagsCloudModule(BaseUIModule):

    def render(self, tags):
        return self.render_string('modules/tagcloud.html', tags=tags)


class VoteModule(BaseUIModule):

    def render(self, post):
        return self.render_string("modules/vote.html", post=post)


class NewCommentModule(BaseUIModule):

    def render(self, post, form):
        return self.render_string('modules/newcomment.html', post=post,
            form=form)


class CommentsModule(BaseUIModule):

    def render(self, post, comments, message, form):
        return self.render_string("modules/comments.html", post=post,
            comments=comments, message=message, form=form)


class CommentModule(BaseUIModule):

    def render(self, comment):
        return self.render_string("modules/comment.html", comment=comment)


class LikeCommentModule(BaseUIModule):

    def render(self, comment):
        return self.render_string("modules/likecomment.html", comment=comment)


class DislikeCommentModule(BaseUIModule):

    def render(self, comment):
        return self.render_string("modules/dislikecomment.html",
            comment=comment)


class EditCommentModule(BaseUIModule):

    def render(self, comment):
        return self.render_string("modules/editcomment.html", comment=comment)


class DeleteCommentModule(BaseUIModule):

    def render(self, comment):
        return self.render_string("modules/deletecomment.html",
            comment=comment)
