import os
from django.core.mail import send_mail


def get_all_rfids():
    from core.models.MemberModels import Member
    from core.models.GearModels import Gear

    """Return a list of all the RFIDs currently in use by the system"""
    # TODO: is there a better way to do this? This approach might get slow
    member_rfids = [member.rfid for member in Member.objects.all()]
    gear_rfids = [gear.rfid for gear in Gear.objects.all()]
    # TODO: If any new types of RFIDs are added, make sure to add them here

    all_rfids = member_rfids + gear_rfids
    return all_rfids


def get_email_template(name):
    """Get the absolute path equivalent of going up one level and then into the templates directory"""
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
    f = open(os.path.join(templates_dir, 'emails', f'{name}.txt'))
    template = f.read()
    f.close()
    return template


def notify_admin(title='No Title Provided', message='No message provided'):
    """Send a email notification to the system admins"""
    from_email = "system-noreply@climbingclubuw.org"
    to_email = "admin@climbingclubuw.org"
    send_mail(title, message, from_email, to_email)


def notify_info(title="No Title Provided", message="No message provided"):
    """Send a email notification to the board 'info' email"""
    from_email = "system-noreply@climbingclubuw.org"
    to_email = "info@climbingclubuw.org"
    send_mail(title, message, from_email, to_email)
