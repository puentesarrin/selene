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
    if not opts.db_rs:
        db = pymongo.MongoClient(opts.db_uri)[opts.db_name]
        logging.info('Connected to a MongoDB standalone instance.')
    else:
        db = pymongo.MongoReplicaSetClient(opts.db_uri,
            replicaSet=opts.db_rs_name)[opts.db_name]
        logging.info('Connected to a MongoDB replica set.')
    http_server = tornado.httpserver.HTTPServer(Selene(db))
    tornado.web.ErrorHandler = web.ErrorHandler
    http_server.listen(opts.port)
    logging.info('Web server listening on %s port.' % opts.port)
    if opts.use_pyuv:
        from tornado_pyuv import UVLoop
        IOLoop.configure(UVLoop)
    loop = IOLoop.instance()
    loop.start()
