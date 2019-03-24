from django.test import TestCase
from django.urls import reverse


class ViewTestCase(TestCase):
    def assertStatusCode(self, response, code=200):
        self.assertEqual(response.status_code, code)


class SmokeTest(ViewTestCase):
    """Redirect user to login page with 'follow' since not logged in"""

    def test_home_page_status_code(self):
        response = self.client.get("/kiosk", follow=True)
        self.assertStatusCode(response)

    def test_view_url_by_name(self):
        response = self.client.get(reverse("kiosk:home"), follow=True)
        self.assertStatusCode(response)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("kiosk:home"), follow=True)
        self.assertTemplateUsed(response, "registration/login.html")
