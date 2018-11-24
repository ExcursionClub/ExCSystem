from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import timedelta

from core.models.MemberModels import Member

from build_permissions import build_all as build_permissions


class LoginTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        build_permissions()

    def setUp(self):
        Member.objects.create_member(
            email='testemail@test.com',
            rfid='0000000001',
            membership_duration=timedelta(days=7),
            password='password'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('kiosk:home'))
        self.assertRedirects(response, '/kiosk/login/')

    def test_user_login(self):
        self.client.login(email='testemail@test.com', password='password')

        response = self.client.get(reverse('kiosk:home'))
        # Should not redirect to login page since logged in
        self.assertEqual(response.status_code, 200)

        # Logged in user should be the user that just logged in
        self.assertEqual(str(response.context['user']), 'testemail@test.com')
