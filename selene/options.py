# -*- coding: utf-8 *-*
import base64
import os
import tornado.options


def setup_options(path):
    #HTTP Server
    tornado.options.define("port", default=8081, type=int, help='Server port')

    #Database
    tornado.options.define("db_uri", default="mongodb://localhost:27017",
        type=str, help='MongoDB database URI')
    tornado.options.define("db_name", default="selene", type=str,
        help='MongoDB database name')

    #SMTP
    tornado.options.define('smtp_host', default='smtp.gmail.com', type=str,
        help='SMTP server host')
    tornado.options.define('smtp_port', default=587, type=int,
        help='SMTP server port')
    tornado.options.define('smtp_username', type=str, help='SMTP user')
    tornado.options.define('smtp_password', type=str, help='SMTP password')
    tornado.options.define('smtp_use_tls', default=True, type=bool,
        help='SMTP use TLS flag')

    #Blog
    tornado.options.define('base_url', default='http://localhost:8081',
        type=str, help='Base URL')
    tornado.options.define('title', default='Selene', type=str,
        help='Blog title')
    tornado.options.define('slogan', default=('A simple CMS for blogging built'
        ' with Tornado and MongoDB'), type=str, help='Blog slogan')
    tornado.options.define('default_language', default='en_US', type=str,
        help='Default language')
    tornado.options.define('page_size_posts', default=10, type=int,
        help='Page size for posts')
    tornado.options.define('page_size_tag_posts', default=10, type=int,
        help='Page size for tag showing posts')
    tornado.options.define('page_size_search_posts', default=10, type=int,
        help='Page size for searching posts')
    tornado.options.define('tag_cloud_limit', default=20, type=int,
        help='Limit for items on tag cloud module')
    tornado.options.define('recent_posts_limit', default=10, type=int,
        help='Limit for items on recent posts module')
    tornado.options.define('recent_comments_limit', default=10, type=int,
        help='Limit for items on recent comments module')

    #Application settings
    tornado.options.define('cookie_secret', default='', type=str)
    tornado.options.define("debug", default=True, type=bool, help=(
        'Turn on autoreload, log to stderr only'))
    tornado.options.define('theme_path', default='theme', type=str,
        help='Theme directory')
    tornado.options.define('static_url_prefix', default=None, type=str,
        help='Static files prefix')

    #Locale
    tornado.options.define('default_locale', default='en', type=str,
        help='Default locale setting')

    #Twitter share
    tornado.options.define('twitter_consumer_key', default=None, type=str,
        help='Twitter consumer key for authentication')
    tornado.options.define('twitter_consumer_secret', default=None, type=str,
        help='Twitter consumer secret for authentication')

    #Twitter auth
    tornado.options.define('twitter_button_enabled', default=True, type=bool,
        help='Twitter share button enabled')
    tornado.options.define('twitter_button_counter', default='vertical',
        type=str, help='Twitter share button counter')
    tornado.options.define('twitter_button_via', type=str,
        help='Twitter share button data via')
    tornado.options.define('twitter_button_hashtags', type=str,
        help='Twitter share button data hashtags')
    tornado.options.define('twitter_button_large', default=False, type=bool,
        help='Twitter share button large size')
    tornado.options.define('twitter_button_title_post_only', default=True,
        type=bool, help=('Twitter share button title post only, without blog '
        'title'))

    #Facebook share
    tornado.options.define('facebook_button_enabled', default=True, type=bool,
        help='Facebook share button enabled')
    tornado.options.define('facebook_button_send', default=False, type=bool,
        help='Facebook share button send option')
    tornado.options.define('facebook_button_style', default='box_count',
        type=str, help='Facebook share button layout style')
    tornado.options.define('facebook_button_width', default=450, type=int,
        help='Facebook share button width')
    tornado.options.define('facebook_button_faces', default=False, type=bool,
        help='Facebook share button show faces flag')
    tornado.options.define('facebook_button_font', type=str,
        help='Facebook share button font')
    tornado.options.define('facebook_button_color', default='light', type=str,
        help='Facebook share button color scheme')
    tornado.options.define('facebook_button_verb', default='like', type=str,
        help='Facebook share button verb to display')

    #Google+ share
    tornado.options.define('googleplus_button_enabled', default=True, type=bool,
        help='Google+ share button enabled')
    tornado.options.define('googleplus_button_size', default='tall', type=str,
        help='Google+ share button size')
    tornado.options.define('googleplus_button_annotation', default='bubble',
        type=str, help='Google+ share button annotation')
    tornado.options.define('googleplus_button_width', default=300,
        type=int, help='Google+ share button width')

    #Disqus
    tornado.options.define('disqus_enabled', default=False, type=bool,
        help='Disqus widget enabled')
    tornado.options.define('disqus_shortname', type=str,
        help='Disqus short name')

    if os.path.exists(path):
        tornado.options.parse_config_file(path)
    else:
        raise ValueError('No config file at %s' % path)

    tornado.options.parse_command_line()

    if not tornado.options.options.cookie_secret:
        tornado.options.options.cookie_secret = base64.b64encode(os.urandom(32))
    return tornado.options.options
