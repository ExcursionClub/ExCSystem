from core.models.MemberModels import Member
from django.db import models

# Create your models here.


class RfidCheckManager(models.Manager):
    @staticmethod
    def create(rfid=None):

        matching_members = list(Member.objects.filter(rfid=rfid))
        num_members = len(matching_members)

        if num_members > 1:
            message = "Multiple Members with this RFID!"
            is_valid = False
        elif num_members == 0:
            message = "Not a member RFID"
            is_valid = False
        else:
            member = matching_members[0]
            message = f"{member.get_full_name()}: {member.group}"
            if member.is_active_member:
                is_valid = True
            else:
                is_valid = False

        check_entry = MemberRFIDCheck(
            rfid_checked=rfid, was_valid=is_valid, message=message
        )
        check_entry.save()
        return is_valid


class MemberRFIDCheck(models.Model):
    objects = RfidCheckManager()

    rfid_checked = models.CharField(max_length=12)
    was_valid = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.CharField(max_length=100)
