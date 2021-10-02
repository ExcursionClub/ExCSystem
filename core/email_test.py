import smtplib
import sib_api_v3_sdk
from uwccsystem import settings
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.EMAIL_API_KEY


def send_email():

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    email = {
        "to": ['tomekmfraczek95@gmail.com'],
        "reply_to": 'test@climbingclubuw.org',
        "sender": {
            "name": 'Testing UWCC',
            "email": 'test@climbingclubuw.org'
        },
        "html_content": 'This test was successful, \nthanks for participating!',
        "subject": 'Test'
    }

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**email)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        raise e


send_email()