from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import timedelta

from core.models.MemberModels import Member


class LoginTest(TestCase):
    def setUp(self):
        Member.objects.create_member(
            email='testemail@test.com',
            rfid='0000000001',
            membership_duration=timedelta(days=7),
            password='password'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, '/kiosk/login/')

    def test_user_login(self):
        c = Client()
        c.login(email='testemail@test.com', password='password')

        response = c.get(reverse('home'))
        # Should not redirect to login page since logged in
        self.assertEqual(response.status_code, 200)

        # TODO: Test if the logged in user matches 'testemail@test.com'
