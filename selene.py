# -*- coding: utf-8 *-*
import tornado.web
import tornado.options
import tornado.httpserver
from tornado.options import define, options
import pymongo
import os
import base64
from xml.dom import minidom
from selene import handlers
from selene import modules
from selene.helpers.xmlhelper import xmldom2dict

define("debug", default=True, type=bool)
define("port", default=8081, type=int)
define("connectionuri", default="mongodb://localhost:27017", type=str)
define("database", default="selene", type=str)


class Selene(tornado.web.Application):

    def set_locales(self):
        self.locales = dict()
        for lang in filter(lambda x: x != "#attributes"
            and not x.endswith("-attrs"),
            self.selene["locales"].keys()):
            self.locales[lang] = self.selene["locales"][lang + "-attrs"]
            self.locales[lang]["code"] = lang
            self.locales[lang]["name"] = self.selene["locales"][lang]
        default_locale = self.selene["locales"]["#attributes"]["default"]
        self.default_locale = self.locales[default_locale]

    def __init__(self):
        self.xml = minidom.parse("config.xml")
        self.config = xmldom2dict(self.xml)["#document"]["configuration"]
        self.selene = self.config["selene"]
        self.blog = self.config["blog"]
        self.set_locales()
        self.db = pymongo.Connection(options.connectionuri)[options.database]
        self.path = os.path.dirname(__file__)
        settings = {
            'static_path': os.path.join(self.path, "static"),
            'template_path': os.path.join(self.path, "templates"),
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
    tornado.locale.load_translations("translations")
    tornado.web.ErrorHandler = handlers.ErrorHandler
    http_server = tornado.httpserver.HTTPServer(Selene())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
