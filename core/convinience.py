from core.models.GearModels import Gear
from django.core.mail import send_mail
from core.models.MemberModels import Member


def get_all_rfids():
    """Return a list of all the RFIDs currently in use by the system"""
    # TODO: is there a better way to do this? This approach might get slow
    member_rfids = [member.rfid for member in Member.objects.all()]
    gear_rfids = [gear.rfid for gear in Gear.objects.all()]
    # TODO: If any new types of RFIDs are added, make sure to add them here

    all_rfids = member_rfids + gear_rfids
    return all_rfids



def notify_admin(title='No Title Provided', message='No message provided'):
    """Send a email notification to the system admins"""
    from_email = 'system-noreply@excursionclubucsb.org'
    to_email = 'admin@excursionclubucsb.org'
    send_mail(title, message, from_email, to_email)


def notify_info(title='No Title Provided', message='No message provided'):
    """Send a email notification to the board 'info' email"""
    from_email = 'system-noreply@excursionclubucsb.org'
    to_email = 'info@excursionclubucsb.org'
    send_mail(title, message, from_email, to_email)

