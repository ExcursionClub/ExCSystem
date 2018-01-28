from core.models.MemberModels import Member
from core.models.GearModels import Gear


def get_all_rfids():
    """Return a list of all the RFIDs currently in use by the system"""
    # TODO: is there a better way to do this? This approach might get slow
    member_rfids = [member.rfid for member in Member.objects.all()]
    gear_rfids = [gear.rfid for gear in Gear.objects.all()]
    # TODO: If any new types of RFIDs are added, make sure to add them here

    all_rfids = member_rfids + gear_rfids
    return all_rfids