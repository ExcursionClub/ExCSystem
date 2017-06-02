from django.db import models


class Gear(models.Model):
    """
    The base model for a piece of gear
    """
    rfid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    is_brokem = models.BooleanField(default=False)
