# -*- coding: utf-8 *-*
import os
import tornado.web

from selene import ui_modules, routes, smtp
from tornado.options import options as opts


class Selene(tornado.web.Application):

    def __init__(self, db):
        self.db = db
        self.smtp = smtp.SMTP()
        self.path = os.path.dirname(__file__)
        settings = {
            'login_url': '/login',
            'static_path': os.path.join(opts.theme_path, 'static'),
            'template_path': os.path.join(opts.theme_path, 'templates'),
            'xsrf_cookies': True,
            'cookie_secret': opts.cookie_secret,
            'ui_modules': ui_modules
        }
        opts.db_use_fts = (opts.db_use_fts and
            'text' in db.command("listCommands")['commands'])
        if opts.static_url_prefix:
            settings['static_url_prefix'] = opts.static_url_prefix
        if opts.twitter_consumer_key and opts.twitter_consumer_secret:
            settings['twitter_consumer_key'] = opts.twitter_consumer_key
            settings['twitter_consumer_secret'] = opts.twitter_consumer_secret
        tornado.web.Application.__init__(self, routes.urls +
            [(r"/(favicon\.ico)", tornado.web.StaticFileHandler,
            {'path': settings['static_path']})], **settings)
