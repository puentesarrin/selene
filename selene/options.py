# -*- coding: utf-8 *-*
import base64
import logging
import os
import tornado.locale

from tornado.options import (define, options, parse_command_line,
                             parse_config_file)

TEXT_TYPES = [('text', 'Text plain'), ('html', 'HTML'), ('md', 'Markdown'),
    ('rst', 'reStructuredText'), ('bbcode', 'BBCode'), ('textile', 'Textile'),
    ('mediawiki', 'MediaWiki'), ('creole', 'Creole')]
STATUSES = [('published', 'Published'), ('unpublished', 'Unpublished')]
STOP_WORDS = 'a,an,are,as,at,be,by,for,in,is,of,on,or,that,to,was'.split(',')
TWITTER_COUNTER = ['none', 'horizontal', 'vertical']


def get_allowed_text_types():
    result = []
    for code, name in TEXT_TYPES:
        if code in options.allowed_text_types:
            result.append((code, name))
    return result


def get_allowed_languages():
    return sorted([(k, v['name_en']) for k, v in
        list(tornado.locale.LOCALE_NAMES.items()) if k in
        tornado.locale.get_supported_locales()])


def get_rtl_languages():
    return ['ar_AR']


def define_options():
    #Tornado
    group = 'Tornado'
    define("use_pyuv", default=False, type=bool,
           help=('Configure IOLoop for using libuv, needs tornado_pyuv '
                 'installed; useful on Windows environments.'), group=group)

    #HTTP Server
    group = 'HTTP Server'
    define("port", default=8081, type=int, help='HTTP server port',
           group=group)

    #Database
    group = 'Database'
    define("db_uri", default="mongodb://localhost:27017", type=str,
           help='MongoDB database URI', group=group)
    define("db_rs", default=False, type=bool,
           help='MongoDB use a replication strategy', group=group)
    define("db_rs_name", default="rs0", type=str,
           help='MongoDB replication name', group=group)
    define("db_name", default="selene", type=str, help='MongoDB database name',
           group=group)
    define("db_use_fts", default=False, type=bool,
           help=('MongoDB full text search activated for searching posts, if '
                 'it is not activated on server, regex will be used'),
           group=group)

    #SMTP
    group = 'SMTP'
    define('smtp_host', default='smtp.gmail.com', type=str,
           help='SMTP server host', group=group)
    define('smtp_port', default=587, type=int, help='SMTP server port',
           group=group)
    define('smtp_username', type=str, help='SMTP user', group=group)
    define('smtp_password', type=str, help='SMTP password', group=group)
    define('smtp_use_tls', default=True, type=bool, help='SMTP use TLS flag',
           group=group)

    #Blog
    group = 'Blog'
    define('base_url', default='http://localhost:8081', type=str,
           help='Base URL', group=group)
    define('title', default='Selene', type=str, help='Blog title', group=group)
    define('slogan', default=('A simple CMS for blogging built with Tornado '
           'and MongoDB'), type=str, help='Blog slogan', group=group)
    define('default_language', default='en_US', type=str,
           help='Default language', group=group)
    define('allowed_text_types', default=[tt[0] for tt in TEXT_TYPES],
           type=str, multiple=True, help='Allowed text types on posts',
           group=group)
    define('slug_stop_words', default=STOP_WORDS, type=str, multiple=True,
           help='Stop words, these will be removed/ignored from post slugs',
           group=group)
    define('page_size_posts', default=10, type=int, help='Page size for posts',
           group=group)
    define('page_size_tag_posts', default=10, type=int,
           help='Page size for tag showing posts', group=group)
    define('page_size_search_posts', default=10, type=int,
           help='Page size for searching posts', group=group)
    define('tag_cloud_limit', default=20, type=int,
           help='Limit for items on tag cloud module', group=group)
    define('recent_posts_limit', default=10, type=int,
           help='Limit for items on recent posts module', group=group)
    define('recent_comments_limit', default=10, type=int,
           help='Limit for items on recent comments module', group=group)

    #Application
    group = 'Application'
    define('cookie_secret', default='', type=str, group=group)
    define("debug", default=False, type=bool, help=('Turn on autoreload, log '
           'to stderr only'), group=group)
    define('themes_directory', default='themes', type=str,
           help='Themes directory name', group=group)
    define('selected_theme', default='default', type=str,
           help='Selected theme directory name', group=group)
    define('static_url_prefix', default=None, type=str,
           help='Static files prefix', group=group)
    define('logging_db', default=False, type=bool,
           help='Enable logging on MongoDB database', group=group)
    define('logging_db_uri', default='mongodb://localhost:27017', type=str,
           help='MongoDB database uri for logging', group=group)
    define('logging_db_name', default='selene_log', type=str,
           help='MongoDB database name for logging', group=group)
    define('logging_db_collection', default='log', type=str,
           help='MongoDB collection name for logging', group=group)

    #Locale
    group = 'Locale'
    define('default_locale', default='en_US', type=str,
           help='Default locale setting', group=group)

    #Google Analytics
    group = 'Google Analytics'
    define("googleanalytics_enabled", default=True, type=bool,
           help="Enable Google Analytics module", group=group)
    define("googleanalytics_enabled_for_logged_users", default=False,
           type=bool, help="Enable Google Analytics module", group=group)
    define("googleanalytics_trackercode", default="UA-XXXXXXXX-X", type=str,
           help='Set Google Analytics tracker code', group=group)

    #Gravatar
    group = 'Gravatar'
    define('gravatar_for_posts', default=True, type=bool,
           help='Enable Gravatar images on posts', group=group)
    define('gravatar_for_comments', default=True, type=bool,
           help='Enable Gravatar images on comments', group=group)

    #Twitter auth
    group = 'Twitter auth'
    define('twitter_consumer_key', default=None, type=str,
           help='Twitter consumer key for authentication', group=group)
    define('twitter_consumer_secret', default=None, type=str,
           help='Twitter consumer secret for authentication', group=group)

    #Twitter share button
    group = 'Twitter share button'
    define('twitter_button_enabled', default=True, type=bool,
           help='Twitter share button enabled', group=group)
    define('twitter_button_counter', default='vertical', type=str,
           help='Twitter share button counter style',
           metavar='|'.join(TWITTER_COUNTER), group=group)
    define('twitter_button_via', type=str,
           help='Twitter share button data via', group=group)
    define('twitter_button_hashtags', type=str,
           help='Twitter share button data hashtags', group=group)
    define('twitter_button_large', default=False, type=bool,
           help='Twitter share button large size', group=group)
    define('twitter_button_title_post_only', default=True, type=bool,
           help='Twitter share button title post only, without blog title',
           group=group)

    #Facebook share
    group = 'Facebook share button'
    define('facebook_button_enabled', default=True, type=bool,
           help='Facebook share button enabled', group=group)
    define('facebook_button_send', default=False, type=bool,
           help='Facebook share button send option', group=group)
    define('facebook_button_style', default='box_count', type=str,
           help='Facebook share button layout style', group=group)
    define('facebook_button_width', default=450, type=int,
           help='Facebook share button width', group=group)
    define('facebook_button_faces', default=False, type=bool,
           help='Facebook share button show faces flag', group=group)
    define('facebook_button_font', type=str,
           help='Facebook share button font', group=group)
    define('facebook_button_color', default='light', type=str,
           help='Facebook share button color scheme', group=group)
    define('facebook_button_verb', default='like', type=str,
           help='Facebook share button verb to display', group=group)

    #Google+ share
    group = 'Google+ share button'
    define('googleplus_button_enabled', default=True, type=bool,
           help='Google+ share button enabled', group=group)
    define('googleplus_button_size', default='tall', type=str,
           help='Google+ share button size', group=group)
    define('googleplus_button_annotation', default='bubble', type=str,
           help='Google+ share button annotation', group=group)
    define('googleplus_button_width', default=300, type=int,
           help='Google+ share button width', group=group)

    #Disqus
    group = 'Disqus'
    define('disqus_enabled', default=False, type=bool, group=group,
           help='Disqus widget enabled')
    define('disqus_shortname', type=str, group=group, help='Disqus short name')


def setup_options(path):
    define_options()
    if os.path.exists(path):
        parse_config_file(path)
    else:
        raise ValueError('No config file at %s' % path)
    parse_command_line()
    if not options.cookie_secret:
        options.cookie_secret = base64.b64encode(os.urandom(32))
        logging.warning('Selene will use a random cookie_secret: %s' %
                        options.cookie_secret)
    return options
