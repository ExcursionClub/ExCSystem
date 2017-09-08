from django.db import models


class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    class Meta:
        verbose_name_plural = "Gear"

    rfid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    status_choices = [
        (0, "In Stock"),
        (1, "Checked Out"),
        (2, "Broken"),
        (3, "Missing"),
        (4, "Dormant"),
        (5, "Removed"),
    ]
    status = models.IntegerField(choices=status_choices)

    def is_available(self):
        """Returns True if the gear is available for renting"""
        if self.status == 0:
            return True
        else:
            return False

    def is_active(self):
        """Returns True if the gear is actively in circulation (ie could be checked out in a few days)"""
        if self.status <= 1:
            return True
        else:
            return False

    def is_existent(self):
        """Returns True if the gear has not been removed or lost"""
        if self.status <= 3:
            return True
        else:
            return False

