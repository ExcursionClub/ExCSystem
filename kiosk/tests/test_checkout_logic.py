from build_permissions import build_all as build_permissions
from core.models.DepartmentModels import Department
from core.models.GearModels import Gear, GearType
from core.models.MemberModels import Member
from core.models.TransactionModels import Transaction
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import timedelta
from kiosk.CheckoutLogic import do_checkin, do_checkout

ADMIN_RFID = '0000000000'
MEMBER_RFID1 = '0000000001'
MEMBER_RFID2 = '0000000002'
GEAR_RFID = '0123456789'


class CheckoutLogicTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        build_permissions()

    def setUp(self):
        Member.objects.create_superuser(
            'john@bro.com',
            ADMIN_RFID,
            'pass'
        )

        member = Member.objects.create_member(
            email='testemail@test.com',
            rfid=MEMBER_RFID1,
            membership_duration=timedelta(days=7),
            password='password'
        )

        other_member = Member.objects.create_member(
            email='testemail2@test.com',
            rfid=MEMBER_RFID2,
            membership_duration=timedelta(days=7),
            password='password'
        )

        member.group = Group.objects.get(name="Member")
        member.first_name = "Jo"
        member.last_name = "McTester1"
        member.save()

        other_member.group = Group.objects.get(name="Member")
        other_member.first_name = "Jo"
        other_member.last_name = "McTester2"
        other_member.save()

        department = Department.objects.create(name='Camping', description='oops')

        gear_type = GearType(
            name='Crash Pad',
            department=department
        )
        gear_type.save()

        _, gear = Transaction.objects.add_gear(
            authorizer_rfid=ADMIN_RFID,
            gear_rfid=GEAR_RFID,
            gear_name='test bag',
            gear_department=department,
            geartype=gear_type,
            gear_image=None,
        )

    def test_checkout_gear(self):
        """Test checkout of available gear to active member by valid staffer succeeds"""
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)

    def test_checkout_gear_to_self(self):
        """Test checkout of available gear to valid staffer by valid staffer succeeds"""
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        do_checkout(ADMIN_RFID, ADMIN_RFID, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)

    def test_checkout_to_new_member(self):
        """Test checkout of available gear to new member by valid staffer fails"""
        member = Member.objects.get(rfid=MEMBER_RFID1)
        member.group = Group.objects.get(name="Just Joined")
        member.save()
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        with self.assertRaises(ValidationError):
            do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), False)

    def test_checkout_to_expired_member(self):
        """Test checkout of available gear to expired member by valid staffer fails"""
        member = Member.objects.get(rfid=MEMBER_RFID1)
        member.group = Group.objects.get(name="Expired")
        member.save()
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        with self.assertRaises(ValidationError):
            do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), False)

    def test_checkout_by_unauthorized_member(self):
        """Test checkout of available gear to active member by unauthorized member fails"""
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        with self.assertRaises(ValidationError):
            do_checkout(MEMBER_RFID1, MEMBER_RFID2, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), False)

    def test_checkout_of_checked_out_gear(self):
        """Do checkout then test checkout of checked out gear to active member by valid staffer fails"""
        do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)
        with self.assertRaises(ValidationError):
            do_checkout(ADMIN_RFID, MEMBER_RFID2, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)

    def test_checkout_of_nonexistent_gear(self):
        """Test checkout of nonexistent gear to active member by valid staffer fails"""
        with self.assertRaises(Gear.DoesNotExist):
            do_checkout(ADMIN_RFID, MEMBER_RFID1, '0123456780')

    def test_checkout_to_nonexistent_member(self):
        """Test checkout of available gear to nonexistent member by valid staffer fails"""
        with self.assertRaises(Member.DoesNotExist):
            do_checkout(ADMIN_RFID, '0000010002', GEAR_RFID)

    def test_checkout_by_nonexistent_member(self):
        """Test checkout of available gear to active member by nonexistent member fails"""
        with self.assertRaises(Member.DoesNotExist):
            do_checkout('0000010002', MEMBER_RFID1, GEAR_RFID)

    def test_checkin_gear(self):
        """Do checkout then test checkin of checked out gear by valid staffer succeeds"""
        do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        do_checkin(ADMIN_RFID, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)

    def test_checkin_gear_by_unauthorized_member(self):
        """Do checkout then test checkin of checked out gear by unauthorized member fails"""
        do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        with self.assertRaises(ValidationError):
            do_checkin(MEMBER_RFID1, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)

    def test_checkin_gear_by_nonexistent_member(self):
        """Do checkout then test checkin of checked out gear by nonexistent member fails"""
        do_checkout(ADMIN_RFID, MEMBER_RFID1, GEAR_RFID)
        with self.assertRaises(Member.DoesNotExist):
            do_checkin('0000010002', GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_rented_out(), True)

    def test_checkin_of_already_returned_gear(self):
        """Test checkin of available gear by valid staffer is fine"""
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
        do_checkin(ADMIN_RFID, GEAR_RFID)
        gear = Gear.objects.get(rfid=GEAR_RFID)
        self.assertEqual(gear.is_available(), True)
