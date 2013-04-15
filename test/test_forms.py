# -*- coding: utf-8 *-*
import unittest

from selene import forms


class TestRegisterForm(unittest.TestCase):

    def setUp(self):
        pass

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
        self.assertEqual(form.full_name.label.text, 'Nombre completo')
