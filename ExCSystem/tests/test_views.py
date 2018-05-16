from django.test import TestCase
from django.urls import reverse
from kiosk import views


class ViewTestCase(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


class SmokeTest(ViewTestCase):
    def test_kiosk(self):
        response = self.client.get(reverse('kiosk'))
        self.assertStatusCode(response)
