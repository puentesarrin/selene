# -*- coding: utf-8 *-*
import logging
import motor
import tornado.web
import tornado.httpserver

from tornado.options import options as opts
from selene import options, Selene, web


if __name__ == '__main__':
    options.setup_options('selene.conf')
    db = motor.MotorClient(opts.db_uri).open_sync()[opts.db_name]
    logging.info('Connected to MongoDB.')
    tornado.locale.load_translations("translations")
    tornado.locale.set_default_locale(opts.default_locale)
    logging.info('Loaded translations: %s.' %
        ', '.join(tornado.locale.get_supported_locales()))
    http_server = tornado.httpserver.HTTPServer(Selene(db))
    tornado.web.ErrorHandler = web.ErrorHandler
    http_server.listen(opts.port)
    logging.info('Listening on %s port.' % opts.port)
    tornado.ioloop.IOLoop.instance().start()
