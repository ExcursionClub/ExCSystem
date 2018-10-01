from django import forms

from core.models.GearModels import Gear


class HomeForm(forms.Form):
    rfid = forms.CharField(max_length=10)


class RetagGearForm(forms.ModelForm):
    class Meta:
        model = Gear
        fields = ['geartype', 'rfid']
