# -*- coding: utf-8 *-*
import tornado.locale

from wtforms import Form


class BaseForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', locale_code='en_US',
        **kwargs):
        self._locale_code = locale_code
        super(BaseForm, self).__init__(formdata, obj, prefix, **kwargs)

    def _get_translations(self):
        if not hasattr(self, '_locale_code'):
            self._locale_code = 'en_US'
        return TornadoLocaleWrapper(self._locale_code)


class TornadoLocaleWrapper(object):

    def __init__(self, code):
        self.locale = tornado.locale.get(code)

    def gettext(self, message):
        return self.locale.translate(message)

    def ngettext(self, message, plural_message, count):
        return self.locale.translate(message, plural_message, count)


from selene.forms.auth_forms import *
from selene.forms.blog_forms import *
