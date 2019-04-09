from django.db import models


class RFIDField(models.CharField):
    """
    Very simple model field specifically designed to store RFID's.

    Essentially just a thin wrapper around CharField that forces the RFID to be unique and ensures that it has at most
    10 characters.
    """

    description = "Specific type of charfield for storing 10 digit RFID's"

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 10
        kwargs["unique"] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        del kwargs["unique"]
        return name, path, args, kwargs
