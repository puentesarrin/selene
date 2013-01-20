# -*- coding: utf-8 *-*
import base64
import os
import tornado.options


def setup_options(path):
    #HTTP Server
    tornado.options.define("port", default=8081, type=int, help='Server port')
    tornado.options.define("db_uri", default="mongodb://localhost:27017",
        type=str, help='MongoDB database URI')
    tornado.options.define("db_name", default="selene", type=str,
        help='MongoDB database name')

    #Blog
    tornado.options.define('base_url', default='Selene', type=str,
        help='Base URL')
    tornado.options.define('title', default='Selene', type=str,
        help='Blog title')
    tornado.options.define('slogan', default=('A simple CMS for blogging built'
        ' with Tornado and MongoDB'), type=str, help='Blog slogan')
    tornado.options.define('default_language', default='en_US', type=str,
        help='Default language')

    #Application settings
    tornado.options.define('cookie_secret',
        default=base64.b64encode(os.urandom(32)), type=str)
    tornado.options.define("debug", default=True, type=bool, help=(
        'Turn on autoreload, log to stderr only'))
    tornado.options.define('theme_path', default='theme', type=str,
        help='Theme directory')

    #Locale
    tornado.options.define('default_locale', default='en', type=str,
        help='Default locale setting')

    if os.path.exists(path):
        tornado.options.parse_config_file(path)
    else:
        raise ValueError('No config file at %s' % path)

    tornado.options.parse_command_line()
    return tornado.options.options
