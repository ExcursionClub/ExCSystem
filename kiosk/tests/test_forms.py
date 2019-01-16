from django.test import TestCase
from kiosk.forms import HomeForm


class FormTest(TestCase):

    def test_valid_home_form(self):
        data = {'rfid': '1234567890'}
        form = HomeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_blank_home_form(self):
        data = {'rfid': ''}
        form = HomeForm(data=data)
        self.assertFalse(form.is_valid())

    def test_invalid_home_form(self):
        data = {'rfid': '01234567890'}
        form = HomeForm(data=data)
        self.assertFalse(form.is_valid())
