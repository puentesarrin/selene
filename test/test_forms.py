# -*- coding: utf-8 *-*
import unittest

from selene import forms


class TestRegisterForm(unittest.TestCase):

    def setUp(self):
        pass

    def test_email_format(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'full_name': 'Gokú',
            'email': 'gokudragonball.gt',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), False)

    def test_missing_fullname(self):
        form = forms.RegisterForm(locale_code='en_US', **{
            'email': 'goku@dragonball.gt',
            'password': 'Nube Kinto'
        })
        self.assertEqual(form.validate(), False)

    def test_spanish_locale(self):
        form = forms.RegisterForm(locale_code='es_ES')
        self.assertEqual(form.full_name.label.text, 'Nombre completo')
