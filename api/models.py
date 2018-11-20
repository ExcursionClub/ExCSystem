from django.db import models

# Create your models here.


class MemberRFIDCheck(models.Model):
    rfid_checked = models.CharField(max_length=12)
    was_valid = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)


