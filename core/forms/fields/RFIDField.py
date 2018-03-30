from django import forms
from django.forms import ValidationError
from ..widgets.RFIDWidget import RFIDWidget


class RFIDField(forms.CharField):
    """
    Wrapper around CharField changing the default widget and adding validation
    """
    widget = RFIDWidget
    rfid_length = 10

    def to_python(self, value):
        """Validate the RFID string is in fact a valid RFID"""

        if value.length != 10:
            raise ValidationError("An RFID must be exactly 10 digits long!")

        if not value.isdigit():
            raise ValidationError("RFIDs may only contain the digits 0-9")

        # If no errors were raised, just let the to_python method of CharField do the actual work.
        return super(RFIDField, self).to_python(value)


