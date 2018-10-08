
import os
import re
from selenium.common import B
import ssl


from __future__ import absolute_import, unicode_literals
from celery import shared_task
from core.models.MemberModels import Member
from get_listserv_email_file import get_active_emails

@shared_task
def test_task():
    print("Tested a task")

@shared_task()
def make_listserv_email_file():
    get_active_emails()