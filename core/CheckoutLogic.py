from django.utils.timezone import now, timedelta

from .models.GearModels import Gear
from .models.MemberModels import Member
from .models.TransactionModels import Transaction


def do_checkout(member_rfid, staffer_rfid, *gear_rfids):
    """
    Manages the checkout of any number of gear objects to a member

    :param member_rfid: rfid string of the member who wishes to check out the gear
    :param staffer_rfid: rfid string of staffer who is validating the transaction
    :param gear_rfids: any number of rfid_strings, one for each piece of gear to be checked out

    :return:
    """

    # TODO: make return date a choose-able parameter, currently just a week from rental date
    return_date = now() + timedelta(days=7)

    for gear_rfid in gear_rfids:
        Transaction.objects.make_checkout(gear_rfid, member_rfid, staffer_rfid, return_date)

