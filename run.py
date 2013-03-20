# -*- coding: utf-8 *-*
import logging
import pymongo
import tornado.web
import tornado.httpserver

from tornado.options import options as opts
from selene import options, handlers, Selene


if __name__ == '__main__':
    options.setup_options('selene.conf')
    db = pymongo.MongoClient(opts.db_uri)[opts.db_name]
    tornado.locale.load_translations("translations")
    tornado.locale.set_default_locale(opts.default_locale)
    http_server = tornado.httpserver.HTTPServer(Selene(db))
    tornado.web.ErrorHandler = handlers.ErrorHandler
    http_server.listen(opts.port)
    logging.info('Listening on %s port.' % opts.port)
    tornado.ioloop.IOLoop.instance().start()
