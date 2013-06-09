# -*- coding: utf-8 *-*
import re
import tornado.locale
import tornado.web

from selene import helpers, options as opts
from tornado.escape import to_unicode
from tornado.options import options
from wtforms import Form


class BaseForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US',
        **kwargs):
        self._locale_code = locale_code
        super(BaseForm, self).__init__(formdata, obj, prefix, **kwargs)

    def process(self, formdata=None, obj=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            formdata = TornadoArgumentsWrapper(formdata)
        super(Form, self).process(formdata, obj, **kwargs)

    def _get_translations(self):
        if not hasattr(self, '_locale_code'):
            self._locale_code = 'en_US'
        return TornadoLocaleWrapper(self._locale_code)


class TornadoArgumentsWrapper(dict):

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError

    def getlist(self, key):
        try:
            values = []
            for v in self[key]:
                v = to_unicode(v)
                if isinstance(v, unicode):
                    v = re.sub(r"[\x00-\x08\x0e-\x1f]", " ", v)
                values.append(v)
            return values
        except KeyError:
            raise AttributeError


class TornadoLocaleWrapper(object):

    def __init__(self, code):
        self.locale = tornado.locale.get(code)

    def gettext(self, message):
        return self.locale.translate(message)

    def ngettext(self, message, plural_message, count):
        return self.locale.translate(message, plural_message, count)


class BaseHandler(tornado.web.RequestHandler):

    @property
    def db(self):
        return self.application.db

    @property
    def smtp(self):
        return self.application.smtp

    def get_current_user(self):
        email = self.get_secure_cookie("current_user") or False
        if not email:
            return None
        return self.db.users.find_one({"email": email})

    def get_user_locale(self):
        user = self.current_user
        if not user:
            locale_cookie = self.get_cookie('locale')
            if locale_cookie in [l[0] for l in opts.get_allowed_languages()]:
                return tornado.locale.get(locale_cookie)
            return None
        if not user["locale"]:
            return None
        return tornado.locale.get(user["locale"])

    def get_template_namespace(self):
        namespace = super(BaseHandler, self).get_template_namespace()
        from selene import forms
        namespace.update({
            'arguments': self.request.arguments,
            'forms': forms,
            'helpers': helpers,
            'options': options,
            'opts': opts,
            'language_choices': opts.get_allowed_languages()
        })
        return namespace

    def render(self, template_name, **kwargs):
        def find_post(comment):
            comment['post'] = self.db.posts.find_one({'_id':
                comment['postid']})
            return comment

        posts = self.db.posts.find({'status': 'published'}).sort('date',
            -1).limit(options.recent_posts_limit)
        comments = self.db.comments.find().sort('date',
            -1).limit(options.recent_comments_limit)
        comments = map(find_post, list(comments))
        tags = self.db.posts.aggregate([
            {'$match': {'status': 'published'}},
            {'$unwind': '$tags'},
            {'$group': {'_id': '$tags', 'sum': {'$sum': 1}}},
            {'$limit': options.tag_cloud_limit}
        ])['result']
        kwargs.update({
            'url_path': self.request.uri,
            '_next': self.get_argument('next', ''),
            '_posts': posts,
            '_comments': comments,
            '_tags': tags
        })
        super(BaseHandler, self).render(template_name, **kwargs)


class BaseUIModule(tornado.web.UIModule):
    pass
