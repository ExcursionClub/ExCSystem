from helper_scripts import setup_django
import uwccsystem.settings as settings
import time
import ssl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions, wait

from core.convinience import notify_info
from core.models.MemberModels import Member

LOAD_WAIT_SECS = 10


def get_active_emails():
    members = Member.objects.all()
    emails = [f"{member.email}\n" for member in members if member.is_active_member]
    return emails


def write_emails(email_list):
    filename = "listserv_emails.txt"
    with open(filename, "w") as email_file:
        email_file.writelines(email_list)
    return filename


def get_email_file():
    emails = get_active_emails()
    filename = write_emails(emails)
    return filename


def push_to_listserv(emails_file):

    profile = webdriver.FirefoxProfile()
    profile.accept_untrusted_certs = True
    profile.assume_untrusted_cert_issuer = True
    capabilities = webdriver.DesiredCapabilities().FIREFOX.copy()
    capabilities["acceptInsecureCerts"] = True
    browser = webdriver.Firefox(firefox_profile=profile, capabilities=capabilities)
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    # Open login page and wait till it loads
    browser.get(settings.LISTSERV_FORM_ADDRESS)
    wait.WebDriverWait(browser, 10).until(
        expected_conditions.element_to_be_clickable((By.XPATH, "//form/p/input[1]"))
    )

    # Submit login info
    email_field = browser.find_element_by_id("Email Address")
    email_field.clear()
    email_field.send_keys(settings.LISTSERV_USERNAME)
    password_field = browser.find_element_by_id("Password")
    password_field.clear()
    password_field.send_keys(settings.LISTSERV_PASSWORD)
    email_field.submit()

    # Wait for login request to complete
    wait.WebDriverWait(browser, 10).until(
        expected_conditions.element_to_be_clickable((By.ID, "Input File"))
    )

    # Open the email upload page and submit the form
    replace_all_button = browser.find_element_by_id("radiob")
    replace_all_button.click()
    file_upload = browser.find_element_by_id("Input File")

    file_upload.send_keys(emails_file)

    print("Waiting for file upload...")
    time.sleep(LOAD_WAIT_SECS)

    file_upload.submit()

    # TODO: parse response and notify someone
    print("Waiting for listserv to process...")
    time.sleep(LOAD_WAIT_SECS)

    print("pause")
    change_message = browser.find_element_by_class_name("message").text

    return change_message


def run_update():
    emails = get_active_emails()
    email_file = write_emails(emails)
    change_message = push_to_listserv(email_file)
    notify_info("Listserv Updated", change_message)


if __name__ == "__main__":
    run_update()
