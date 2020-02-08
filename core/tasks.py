from helper_scripts import setup_django

from sys import argv

from django.utils.timezone import datetime, timedelta
from datetime import date

from excsystem.settings import GEAR_EXPIRE_TIME
from core.models.MemberModels import Member
from core.models.GearModels import Gear
from core.models.TransactionModels import Transaction


def test_task():
    print("Tested a task")


def update_listserv():
    from helper_scripts import listserv_interface

    listserv_interface.run_update()


def expire_members():

    now = datetime.date(datetime.now())
    expires_in_week = now + timedelta(days=7)

    for member in Member.objects.all():

        # Only check if the member is expired if the are active.
        if member.group == 'Member' or member.group == 'Just Joined':

            # Expire members
            if member.date_expires < now:
                member.expire()
                member.send_expired_email()

            # If members will expire soon, send them an email
            elif member.date_expires == expires_in_week:
                member.send_expires_soon_email()


def expire_gear():
    """"""
    checked_out = Gear.objects.filter(status__in=[1, 3])
    sys_rfid = Member.objects.get(email='system@excursionclubucsb.org').rfid
    today = date.today()
    for gear in checked_out:
        if gear.status == 1 and today > gear.due_date:
            Transaction.objects.missing_gear(sys_rfid, gear.rfid)
        elif gear.status == 3:
            if not gear.due_date:
                gear.due_date = today
            elif today > gear.due_date + GEAR_EXPIRE_TIME:
                Transaction.objects.expire_gear(sys_rfid, gear.rfid)


def email_overdue_gear():
    """Send an email to all members with overdue gear listing all overdue gear"""
    missing = Gear.objects.filter(status=3).order_by('checked_out_to__pk')

    try:
        current_member = missing[0].checked_out_to
    except IndexError:
        return
    members_gear = []

    for gear in missing:
        if gear.checked_out_to.pk != current_member.pk:
            current_member.send_missing_gear_email(members_gear)
            current_member = gear.checked_out_to
            members_gear = [gear]
        else:
            members_gear.append(gear)

    current_member.send_missing_gear_email(members_gear)


if __name__ == "__main__":
    task_name = argv[1].lower()
    if task_name == "test":
        test_task()
    elif task_name == "update_listserv":
        update_listserv()
    elif task_name == "expire_members":
        expire_members()
    elif task_name == "expire_gear":
        expire_gear()
    elif task_name == "email_overdue_gear":
        email_overdue_gear()
    else:
        print(f"Invalid task name: '{task_name}'!")
