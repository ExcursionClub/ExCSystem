from random import randint

from helper_scripts.build_basic_data import *
from core.models.MemberModels import Member
from django.test import Client, TestCase
from django.utils.timezone import timedelta


class MemberRFIDCheckTest(TestCase):

    base_url = '/api/memberRFIDcheck'
    used_rfids = []

    @classmethod
    def setUpTestData(cls):
        build_site()
        build_departments()
        build_certifications()
        build_permissions()

    def make_test_member(self, rfid, group_name):
        member = Member.objects.create_member(
            'test@email.lol',
            rfid,
            timedelta(days=7),
            password='admin'
        )

        member.move_to_group(group_name)
        member.save()

    def gen_rfid(self):
        """get a unique random RFID"""
        rfid = randint(11111111, 99999999)
        if rfid in self.used_rfids:
            rfid = self.gen_rfid()
        else:
            self.used_rfids.append(rfid)
        return rfid

    def do_gate_check(self, rfid):
        client = Client()
        url = f"{self.base_url}/{rfid}"
        return client.get(url)

    def is_valid_member_rfid(self, rfid):
        response = self.do_gate_check(rfid)
        return response.status_code == 200

    def test_random_rfid_not_valid(self):
        was_validated = self.is_valid_member_rfid(self.gen_rfid())
        self.assertFalse(was_validated, "A unregistered RFID should not be considered a valid member!")

    def test_new_member_not_valid(self):
        rfid = self.gen_rfid()
        self.make_test_member(rfid, "Just Joined")
        was_validated = self.is_valid_member_rfid(rfid)
        self.assertFalse(was_validated, "New members should not be valid members!")

    def test_expired_member_not_valid(self):
        rfid = self.gen_rfid()
        self.make_test_member(rfid, "Expired")
        was_validated = self.is_valid_member_rfid(rfid)
        self.assertFalse(was_validated, "Expired members should not be valid members!")

    def test_active_member_is_valid(self):
        rfid = self.gen_rfid()
        self.make_test_member(rfid, "Member")
        was_validated = self.is_valid_member_rfid(rfid)
        self.assertTrue(was_validated, "Active members should be valid members!")

    def test_staffer_is_valid(self):
        rfid = self.gen_rfid()
        self.make_test_member(rfid, "Staff")
        was_validated = self.is_valid_member_rfid(rfid)
        self.assertTrue(was_validated, "Staffers should be valid members!")

    def test_board_member_is_valid(self):
        rfid = self.gen_rfid()
        self.make_test_member(rfid, "Board")
        was_validated = self.is_valid_member_rfid(rfid)
        self.assertTrue(was_validated, "Board members should be valid members!")
