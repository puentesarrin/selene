# -*- coding: utf-8 *-*
import tornado.locale
import unittest

from selene import forms


class TestRegisterForm(unittest.TestCase):

    def setUp(self):
        tornado.locale.LOCALE_NAMES['zh_HK'] = {
            'name_en': 'Chinese (Hong Kong)',
            'name': '\u4e2d\u6587(\u7e41\u9ad4)'
        }
        tornado.locale.load_translations("translations")

    def test_successfully(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'full_name': 'Gokú',
            'email': 'goku@dragonball.gt',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), True)

    def test_email_format(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'full_name': 'Gokú',
            'email': 'gokudragonball.gt',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), False)

    def test_required_fullname(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'email': 'goku@dragonball.gt',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), False)

    def test_required_email(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'full_name': 'Gokú',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), False)

    def test_required_password(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'full_name': 'Gokú',
            'email': 'goku@dragonball.gt',
        })
        self.assertEqual(form.validate(), False)

    def test_spanish_locale(self):
        form = forms.RegisterForm(locale_code='es_ES')
        self.assertEqual(form.full_name.label.text, u'Nombre completo')
        self.assertEqual(form.email.label.text, u'Correo electrónico')
        self.assertEqual(form.password.label.text, u'Contraseña')

    def test_chinese_locale_zh_CN(self):
        form = forms.RegisterForm(locale_code='zh_CN')
        self.assertEqual(form.full_name.label.text, u'完整姓名')
        self.assertEqual(form.email.label.text, u'电子邮箱')
        self.assertEqual(form.password.label.text, u'密码')
