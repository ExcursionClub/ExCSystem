import setupDjango
import ExCSystem.settings as settings
import os
import re
import ssl
from selenium import webdriver

from core.models.MemberModels import Member


def get_active_emails():
    members = Member.objects.all()
    emails = [f"{member.email}\n" for member in members if member.is_active_member]
    return emails


def write_emails(email_list):
    with open("listserv_emails.txt", 'w') as email_file:
        email_file.writelines(email_list)


def push_to_listserv(emails_file):

    browser = webdriver.Firefox()
    browser.addheaders = [('User-agent', 'Firefox')]
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Login in to listserv
    browser.get(settings.LISTSERV_FORM_ADDRESS)
    email_field = browser.find_element_by_id("Email Address")
    email_field.clear()
    email_field.send_keys(settings.LISTSERV_USERNAME)
    password_field = browser.find_element_by_id("Password")
    password_field.clear()
    password_field.send_keys(settings.LISTSERV_PASSWORD)
    email_field.submit()

    # TODO: need to wait for request to complete here

    # Open the email upload page and submit the form
    replace_all_button = browser.find_element_by_id("radiob")
    replace_all_button.click()
    file_upload = browser.find_element_by_id("Input File")
    file_upload.send_keys(emails_file)
    file_upload.submit()

    # TODO: parse response and notify someone


if __name__ == "__main__":
    push_to_listserv("/home/tomek/Work/Excursion/listserv_emails_11-27.txt") #get_active_emails()
