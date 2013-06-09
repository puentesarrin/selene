# -*- coding: utf-8 *-*
import logging
import motor
import tornado.web
import tornado.httpserver

from tornado.ioloop import IOLoop
from tornado.options import options as opts
from selene import log, options, Selene, web


if __name__ == '__main__':
    options.setup_options('selene.conf')
    if not opts.db_rs:
        db = motor.MotorClient(opts.db_uri).open_sync()[opts.db_name]
        logging.info('Connected to a MongoDB standalone instance.')
    else:
        db = motor.MotorReplicaSetClient(opts.db_uri,
            replicaSet=opts.db_rs_name).open_sync()[opts.db_name]
        logging.info('Connected to a MongoDB replica set.')
    if opts.logging_db:
        log.configure_mongolog()
    http_server = tornado.httpserver.HTTPServer(Selene(db))
    tornado.web.ErrorHandler = web.ErrorHandler
    http_server.listen(opts.port)
    logging.info('Web server listening on %s port.' % opts.port)
    if opts.use_pyuv:
        from tornado_pyuv import UVLoop
        IOLoop.configure(UVLoop)
    loop = IOLoop.instance()
    loop.start()
