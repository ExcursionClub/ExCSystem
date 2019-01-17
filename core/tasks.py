from helper_scripts import setup_django

from sys import argv

from django.utils.timezone import datetime, timedelta

from core.models.MemberModels import Member


def test_task():
    print("Tested a task")


def update_listserv():
    from helper_scripts import listserv_interface

    listserv_interface.run_update()


def expire_members():

    now = datetime.date(datetime.now())
    expires_in_week = (now + timedelta(days=6), now + timedelta(days=8))

    for member in Member.objects.all():

        # Only check if the member is expired if the are active.
        if member.group == 'Member' or member.group == 'Just Joined':

            # Expire members
            if member.date_expires < now:
                member.expire()

            # If members will expire soon, send them an email
            elif expires_in_week[0] < member.date_expires < expires_in_week[1]:
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
