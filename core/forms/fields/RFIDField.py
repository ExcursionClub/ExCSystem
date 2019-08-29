from django import forms
from django.forms import ValidationError
from core.forms.widgets import RFIDWidget


class RFIDField(forms.CharField):
    """
    Wrapper around CharField changing the default widget and adding validation
    """

    widget = RFIDWidget

    def __init__(self, max_length=10, min_length=10, **kwargs):
        super().__init__(max_length=max_length, min_length=min_length, **kwargs)

    def to_python(self, value):
        """Validate the RFID string is in fact a valid RFID"""
        if value is None:
            value = ""

        if value and not value.isdigit():
            raise ValidationError("RFIDs may only contain the digits 0-9")

        # If no errors were raised, just let the to_python method of CharField do the actual work.
        return super(RFIDField, self).to_python(value)
