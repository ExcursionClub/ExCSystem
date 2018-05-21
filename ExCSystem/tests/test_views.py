from django.test import TestCase
from django.urls import reverse
from kiosk import views


class ViewTestCase(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


class SmokeTest(ViewTestCase):
    def test_home(self):
        """Redirect user to login page since not logged in"""
        response = self.client.get(reverse('home'))
        self.assertStatusCode(response, code=302)
