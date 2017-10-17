"""All updates that should be regularly executed on the database should be found here"""
from django.utils.timezone import now, timedelta

from core.models.MemberModels import Member, Staffer
from core.models.GearModels import Gear
from core.models.TransactionModels import Transaction


def expire_members():
    """Loops through all the regular members and expires those whose membership has expired"""
    active_members = Member.objects.filter(status=2)
    right_now = now()
    for member in active_members:
        if right_now > member.date_expires:
            member.expire()

# TODO: Once trip logs are implemented, add staffer expiration


def identify_missing_gear():
    """Loops through all the checked out gear and sets as missing any that is checked out past the due date"""
    checked_out = Gear.objects.filter(status=1)
    right_now = now()
    for gear in checked_out:
        if right_now > gear.due_date:
            # Make the gear missing and create the associated transaction
            Transaction.objects.missing_gear("1111111111", gear.rfid)


def expire_gear():
    """Expires any gear that has been missing for a very long time"""
    right_now = now()

    # TODO: What should this time frame be for missing gear?
    expiration_threshold = timedelta(days=3 * 30)  # 3 months
    # Get all the missing gear and check if it is expired
    missing_gear = Gear.objects.filter(status=3)
    for gear in missing_gear:
        if right_now > gear.due_date + expiration_threshold:
            Transaction.objects.expire_gear("1111111111", gear.rfid)

    # TODO: What should this time frame be for broken gear?
    expiration_threshold = timedelta(days=5 * 30)  # 5 months
    # Get all the broken gear and check if it is expired
    missing_gear = Gear.objects.filter(status=2)
    for gear in missing_gear:
        if right_now > gear.due_date + expiration_threshold:
            Transaction.objects.expire_gear("1111111111", gear.rfid)




