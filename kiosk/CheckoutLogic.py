from django.utils.timezone import now, timedelta

from core.models.TransactionModels import Transaction


# TODO: Give option to authorize with a staffer login, not only rfid

def do_checkout(staffer_rfid, member_rfid, *gear_rfids):
    """
    Checkout any number of gear objects to a member

    :param member_rfid: rfid string of the member who wishes to check out the gear
    :param staffer_rfid: rfid string of staffer who is validating the transaction
    :param gear_rfids: any number of rfid_strings, one for each piece of gear to be checked out
    """

    # TODO: make return date a choose-able parameter, currently just a week from rental date
    return_date = now() + timedelta(days=7)

    for gear_rfid in gear_rfids:
        Transaction.objects.make_checkout(staffer_rfid, gear_rfid, member_rfid, return_date)


def do_checkin(staffer_rfid, *gear_rfids):
    """
    Check in any number of pieces of gear to a member

    :param staffer_rfid: rfid string of staffer who is validating the transaction
    :param gear_rfids: any number of rfid_strings, one for each piece of gear to be checked in
    """
    authorizer_rfid = staffer_rfid

    for gear_rfid in gear_rfids:
        Transaction.objects.check_in_gear(authorizer_rfid, gear_rfid)