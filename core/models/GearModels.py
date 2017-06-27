from django.db import models


class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    class Meta:
        verbose_name_plural = "Gear"

    rfid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    is_brokem = models.BooleanField(default=False)
    status_choices = {
        (0, "In Stock"),
        (1, "Checked Out"),
        (2, "Broken"),
        (3, "Missing"),
        (4, "Dormant"),
        (5, "Removed"),
    }
    status = models.IntegerField(choices=status_choices)