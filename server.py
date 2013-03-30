# -*- coding: utf-8 *-*
import logging
import pymongo
import tornado.web
import tornado.httpserver

from tornado.ioloop import IOLoop
from tornado.options import options as opts
from selene import options, Selene, web


if __name__ == '__main__':
    options.setup_options('selene.conf')
    db = pymongo.MongoClient(opts.db_uri)[opts.db_name]
    logging.info('Connected to MongoDB.')
    tornado.locale.load_translations("translations")
    tornado.locale.set_default_locale(opts.default_locale)
    logging.info('Loaded translations: %s.' %
        ', '.join(tornado.locale.get_supported_locales()))
    http_server = tornado.httpserver.HTTPServer(Selene(db))
    tornado.web.ErrorHandler = web.ErrorHandler
    http_server.listen(opts.port)
    logging.info('Listening on %s port.' % opts.port)
    loop = IOLoop.instance()
    if opts.use_pyuv:
        from tornado_pyuv import UVLoop
        IOLoop.configure(UVLoop)
    loop.start()
