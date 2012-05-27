import tornado.web
import tornado.options
import tornado.httpserver
from tornado.options import define, options
import pymongo
import os
import base64
from xml.dom import minidom
import handlers
import modules
from helpers.xmlhelper import xmldom2dict

define("debug", default=True, type=bool)
define("port", default=8081, type=int)
define("database", default="selene", type=str)


class Selene(tornado.web.Application):

    def __init__(self):
        self.xml = minidom.parse("config.xml")
        self.config = xmldom2dict(self.xml)["#document"]["configuration"]
        self.db = pymongo.Connection()[options.database]
        app_path = os.path.dirname(__file__)
        settings = {
            'static_path': os.path.join(app_path, "static"),
            'template_path': os.path.join(app_path, "templates"),
            "ui_modules": modules,
            "cookie_secret": base64.b64encode(os.urandom(32)),
            "login_url": "/login",
            "xsrf_cookies": True,
            'debug': options.debug
            }
        urls = [
            (r"/", handlers.HomeHandler),
            (r"/register/?", handlers.RegisterHandler),
            (r"/login/?", handlers.LoginHandler),
            (r"/logout/?", handlers.LogoutHandler),
            (r"/post/new/?", handlers.NewPostHandler),
            (r"/post/([a-zA-Z0-9-]+)/?", handlers.PostHandler),
            (r"/post/([a-zA-Z0-9-]+)/edit/?", handlers.EditPostHandler),
            (r"/post/delete/?", handlers.DeletePostHandler),
            (r"/rss/?", handlers.RssHandler),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
                 dict(path=settings['static_path']))]
        tornado.web.Application.__init__(self, urls, **settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    tornado.web.ErrorHandler = handlers.ErrorHandler
    http_server = tornado.httpserver.HTTPServer(Selene())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
