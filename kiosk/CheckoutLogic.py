from core.models.TransactionModels import Transaction
from django.utils.timezone import now, timedelta


def do_checkout(staffer_rfid: str, member_rfid: str, gear_rfid: str) -> None:
    # TODO: make return date a choose-able parameter, currently just a week from rental date
    return_date = now().today() + timedelta(days=7)
    Transaction.objects.make_checkout(staffer_rfid, gear_rfid, member_rfid, return_date)


def do_checkin(staffer_rfid: str, gear_rfid: str) -> None:
    Transaction.objects.check_in_gear(staffer_rfid, gear_rfid)
