# -*- coding: utf-8 *-*
from selene import handlers


urls = [
    (r"/", handlers.HomeHandler),
    (r"/page/([0-9]+)", handlers.HomeHandler),
    (r"/register/?", handlers.RegisterHandler),
    (r"/login/?", handlers.LoginHandler),
    (r'/confirm-account/(.*)', handlers.ConfirmAccountHandler),
    (r'/new-password', handlers.RequestNewPasswordHandler),
    (r'/reset-password/(.*)', handlers.ResetPasswordHandler),
    (r"/logout/?", handlers.LogoutHandler),
    (r"/post/new/?", handlers.NewPostHandler),
    (r"/post/([a-zA-Z0-9-]+)/?", handlers.PostHandler),
    (r"/post/([a-zA-Z0-9-]+)/edit/?", handlers.EditPostHandler),
    (r"/post/([a-zA-Z0-9-]+)/delete/?", handlers.DeletePostHandler),
    (r"/post/([a-zA-Z0-9-]+)/vote/?", handlers.VotePostHandler),
    (r'/posts', handlers.PostsHandlers),
    (r'/tag/([a-zA-Z0-9-]+)/?', handlers.TagHandler),
    (r'/tag/([a-zA-Z0-9-]+)/page/([0-9]+)?', handlers.TagHandler),
    (r'/tags', handlers.TagsHandlers),
    (r'/search', handlers.SearchHandler),
    (r'/post/([a-zA-Z0-9-]+)/comment/new', handlers.NewCommentHandler),
    (r'/comment/([a-z0-9]{24})/(like|dislike)', handlers.LikeCommentHandler),
    (r'/comment/([a-z0-9]{24})/edit', handlers.EditCommentHandler),
    (r'/comment/([a-z0-9]{24})/delete', handlers.DeleteCommentHandler),
    (r"/rss/?", handlers.RssHandler)]
