from django import forms


class HomeForm(forms.Form):
    rfid = forms.CharField(max_length=10)