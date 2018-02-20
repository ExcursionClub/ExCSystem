from django.utils.timezone import now, timedelta

from core.models.TransactionModels import Transaction


def do_checkout(staffer_rfid, member_rfid, gear_rfid):
    # TODO: make return date a choose-able parameter, currently just a week from rental date
    return_date = now() + timedelta(days=7)
    Transaction.objects.make_checkout(staffer_rfid, gear_rfid, member_rfid, return_date)


def do_checkin(staffer_rfid, gear_rfid):
    Transaction.objects.check_in_gear(staffer_rfid, gear_rfid)
