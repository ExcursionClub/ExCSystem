from django import forms
from ..widgets.RFIDWidget import RFIDWidget


class RFIDField(forms.CharField):
    """
    Ultra thin wrapper, just sets the default widget to be the RFID widget
    """
    widget = RFIDWidget


