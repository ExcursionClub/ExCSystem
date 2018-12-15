from sys import argv

from django.utils.timezone import datetime, timedelta

from core.models.MemberModels import Member
from listserv_interface import *


def test_task():
    print("Tested a task")


def update_listserv():
    import listserv_interface
    listserv_interface.run_update()


def expire_members():

    now = datetime.now()
    expires_soon_time = now + timedelta(days=7)

    for member in Member.objects.all():

        # Only check if the member is expired if the are active.
        if member.is_active_member:

            # Expire members
            if member.date_expires < now:
                member.expire()

            # If members will expire soon, send them an email
            elif member.date_expires < expires_soon_time:
                member.send_expires_soon_email()


if __name__ == "__main__":
    task_name = argv[1]
    if task_name == "test":
        test_task()
    elif task_name == "updateListserv":
        update_listserv()
    elif task_name == "expireMembers":
        expire_members()
    else:
        print(f"Invalid task name: '{task_name}'!")


