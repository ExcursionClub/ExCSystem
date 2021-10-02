import smtplib
import sib_api_v3_sdk
from uwccsystem import settings
from sib_api_v3_sdk.rest import ApiException

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.EMAIL_API_KEY


def send_email(to_emails, title, body,
               from_email=None, from_name=None, receiver_names=None):

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Prepare the list of recipients, optionally including names
    if receiver_names is None:
        recipients = [{'email': mail} for mail in to_emails]
    else:
        recipients = [{'email': mail, 'name': name} for name, mail in zip(receiver_names, to_emails)]

    email = {
        "to": recipients,
        "reply_to": {'email': from_email},
        "sender": {
            "name": from_name,
            "email": from_email
        },
        "html_content": body,
        "subject": title
    }

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(**email)

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
        raise e


def send_membership_email(to_emails, title, body, receiver_names=None):
    """Send an email from the club membership email. See send_email for more details"""
    send_email(
        to_emails,
        title,
        body,
        receiver_names=receiver_names,
        from_email=settings.MEMBERSHIP_EMAIL,
        from_name='UWCC Membership',
    )
