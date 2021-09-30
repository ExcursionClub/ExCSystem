from core.models.GearModels import Gear
from django import forms


class HomeForm(forms.Form):
    rfid = forms.CharField(
        max_length=10, widget=forms.TextInput(attrs={"placeholder": "    10 digit RFID", "autofocus": "autofocus"})
    )


class RetagGearForm(forms.ModelForm):
    class Meta:
        model = Gear
        fields = ["geartype", "rfid"]
