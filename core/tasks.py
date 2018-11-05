
from __future__ import absolute_import, unicode_literals
from celery import shared_task

from django.utils.timezone import datetime, timedelta

from core.models.MemberModels import Member
from get_listserv_email_file import *


@shared_task
def test_task():
    print("Tested a task")


@shared_task()
def make_listserv_email_file():
    emails = get_active_emails()
    write_emails(emails)


@shared_task
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
