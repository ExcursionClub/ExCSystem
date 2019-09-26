import smtplib
from uwccsystem import settings


def send_email(to_emails, title, body,
               from_email=None, smtp_password=None, from_name='Excursion Club', receiver_names=None):

    # If SMTP credentials are not given, use defaults
    if from_email is None:
        from_email = settings.EMAIL_HOST_USER
    if smtp_password is None:
        smtp_password = settings.EMAIL_HOST_PASSWORD

    # Prepare the list of recipients, optionally including names
    if receiver_names is None:
        recipients = ", ".join([f'<{email}>' for email in to_emails])
    else:
        recipients = ", ".join([f'{receiver[0]} <{receiver[1]}>' for receiver in zip(receiver_names, to_emails)])

    # Prepare the formatted email message ready to be sent
    email = f"""From: {from_name} <{from_email}>
    To: {recipients}
    Subject: {title}
    {body}
    """

    smtp_obj = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    if settings.EMAIL_USE_TLS:
        smtp_obj.starttls()
        smtp_obj.login(from_email, smtp_password)
    smtp_obj.sendmail(from_email, to_emails, email)
    print("Successfully sent email")


def send_membership_email(to_emails, title, body, receiver_names=None):
    """Send an email from the club membership email. See send_email for more details"""
    send_email(
        to_emails,
        title,
        body,
        receiver_names=receiver_names,
        from_email=settings.MEMBERSHIP_EMAIL_HOST_USER,
        from_name='UWCC Membership',
        smtp_password=settings.MEMBERSHIP_EMAIL_HOST_PASSWORD,
    )
