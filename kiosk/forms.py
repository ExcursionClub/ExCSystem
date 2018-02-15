from django import forms


class HomeForm(forms.Form):
    rfid = forms.CharField()