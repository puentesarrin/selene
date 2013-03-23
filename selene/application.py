# -*- coding: utf-8 *-*
import logging
import os
import tornado.web

from selene import ui_modules, routes, smtp
from selene.helpers import string_helper
from tornado.options import options as opts


class Selene(tornado.web.Application):

    def __init__(self, db):
        self.db = db
        self.smtp = smtp.SMTP()
        self.theme_path = os.path.join(opts.themes_directory,
            opts.selected_theme)
        settings = {
            'login_url': '/login',
            'static_path': os.path.join(self.theme_path, 'static'),
            'template_path': os.path.join(self.theme_path, 'templates'),
            'xsrf_cookies': True,
            'cookie_secret': opts.cookie_secret,
            'ui_modules': ui_modules
        }
        string_helper.stop_words = opts.stop_words.split(',')
        if opts.db_use_fts:
            opts.db_use_fts = ('text' in db.command("listCommands")['commands']
                and db.connection.admin.command('getParameter', 1,
                    textSearchEnabled=1)['textSearchEnabled'])
            if not opts.db_use_fts:
                logging.warning('Full text search is probably not activated '
                    'on MongoDB server, If you want to activated it, use 2.4 '
                    'version and issue the following command on admin '
                    'database:\n db.runCommand({ setParameter: 1, '
                    'textSearchEnabled: true })')
            else:
                db.posts.ensure_index([('plain_content', 'text')])
        if opts.static_url_prefix:
            settings['static_url_prefix'] = opts.static_url_prefix
        if opts.twitter_consumer_key and opts.twitter_consumer_secret:
            settings['twitter_consumer_key'] = opts.twitter_consumer_key
            settings['twitter_consumer_secret'] = opts.twitter_consumer_secret
        tornado.web.Application.__init__(self, routes.urls +
            [(r"/(favicon\.ico)", tornado.web.StaticFileHandler,
            {'path': settings['static_path']})], **settings)
