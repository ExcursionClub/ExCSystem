from build_permissions import build_all as build_permissions
from core.models.MemberModels import Member
from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils.timezone import timedelta
from kiosk.views import get_name

MEMBER_RFID = '1234567890'
MEMBER_RFID2 = '2234567890'
FIRST_NAME = 'Jo'
LAST_NAME = 'McTester'
FULL_NAME = f'{FIRST_NAME} {LAST_NAME}'


class HelpMethodTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        build_permissions()

    def setUp(self):
        member = Member.objects.create_member(
            email='testemail@test.com',
            rfid=MEMBER_RFID,
            membership_duration=timedelta(days=7),
            password='password',
        )
        member.group = Group.objects.get(name="Member")
        member.first_name = FIRST_NAME
        member.last_name = LAST_NAME
        member.save()

        Member.objects.create_member(
            email='testemail2@test.com',
            rfid=MEMBER_RFID2,
            membership_duration=timedelta(days=7),
            password='password'
        )

    def test_get_name(self):
        self.assertEqual(get_name(MEMBER_RFID), FULL_NAME)

    def test_get_name_no_name(self):
        self.assertEqual(get_name(MEMBER_RFID2), 'New Member')
