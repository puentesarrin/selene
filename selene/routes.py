# -*- coding: utf-8 *-*
from selene import handlers


urls = [
    (r"/", handlers.HomeHandler),
    (r"/register/?", handlers.RegisterHandler),
    (r"/login/?", handlers.LoginHandler),
    (r'/confirm-account/(.*)', handlers.ConfirmAccountHandler),
    (r'/new-password', handlers.RequestNewPasswordHandler),
    (r'/reset-password/(.*)', handlers.ResetPasswordHandler),
    (r"/logout/?", handlers.LogoutHandler),
    (r"/post/new/?", handlers.NewPostHandler),
    (r"/post/([a-zA-Z0-9-]+)/?", handlers.PostHandler),
    (r"/post/([a-zA-Z0-9-]+)/edit/?", handlers.EditPostHandler),
    (r"/post/delete/?", handlers.DeletePostHandler),
    (r'/posts', handlers.PostsHandlers),
    (r'/tag/([a-zA-Z0-9-]+)/?', handlers.TagHandler),
    (r"/rss/?", handlers.RssHandler)]
