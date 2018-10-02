
import os
import re
from selenium.common import B
import ssl


from __future__ import absolute_import, unicode_literals
from celery import shared_task
from core.models.MemberModels import Member

@shared_task
def test_task():
    print("Tested a task")


def make_listserv_email_file():
    active_members = Member.objects.filter(is_active=True)
    emails = [member.email for member in active_members]

    email_file = open("listserv_emails.txt", 'w')
    email_file.writelines(emails)
    email_file.close()