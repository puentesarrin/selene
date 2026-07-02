from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any

import tornado.ioloop
import tornado.locale
import tornado.web
from tornado.options import options as opts

from selene import smtp
from selene.web import routes, ui_modules

if TYPE_CHECKING:
    from pymongo.asynchronous.database import AsyncDatabase


class Selene(tornado.web.Application):
    def __init__(self, db: AsyncDatabase[Any]):
        self.db = db
        self.smtp = smtp.SMTP()
        self.theme_path = os.path.join(opts.themes_directory, opts.selected_theme)
        self.setup_translations()
        settings = {
            'login_url': '/login',
            'static_path': os.path.join(self.theme_path, 'static'),
            'template_path': os.path.join(self.theme_path, 'templates'),
            'xsrf_cookies': True,
            'cookie_secret': opts.cookie_secret,
            'ui_modules': ui_modules,
            'debug': opts.debug,
        }
        if opts.static_url_prefix:
            settings['static_url_prefix'] = opts.static_url_prefix
        if opts.twitter_consumer_key and opts.twitter_consumer_secret:
            settings['twitter_consumer_key'] = opts.twitter_consumer_key
            settings['twitter_consumer_secret'] = opts.twitter_consumer_secret
        super().__init__(
            [*routes.urls, (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': settings['static_path']})],
            **settings,
        )
        tornado.ioloop.IOLoop.current().spawn_callback(self.setup_fts)

    async def setup_fts(self):
        try:
            await self.db.posts.create_index([('plain_content', 'text')])
        except Exception:
            logging.warning('MongoDB text search could not be enabled. Regex search will be used for queries.')

    def setup_translations(self):
        tornado.locale.LOCALE_NAMES['zh_HK'] = {
            'name_en': 'Chinese (Hong Kong)',
            'name': '中文(繁體)',
        }
        tornado.locale.load_translations('translations')
        tornado.locale.set_default_locale(opts.default_locale)
        supported = sorted(
            [
                v['name_en']
                for k, v in list(tornado.locale.LOCALE_NAMES.items())
                if k in tornado.locale.get_supported_locales()
            ]
        )
        logging.info(f'Loaded translations: {", ".join(supported)}.')
