from django import forms


class HomeForm(forms.Form):
    rfid = forms.CharField(max_length=10)


FRUIT_CHOICES = [
    ('orange', 'Oranges'),
    ('cantaloupe', 'Cantaloupes'),
    ('mango', 'Mangoes'),
    ('honeydew', 'Honeydews'),
    ]


class DepartmentForm(forms.Form):
    favorite_fruit= forms.CharField(label='Select the department the gear is in',
                                    widget=forms.RadioSelect(choices=FRUIT_CHOICES))


class GearForm(forms.Form):
    favorite_fruit= forms.CharField(label='Select what you are retagging',
                                    widget=forms.RadioSelect(choices=FRUIT_CHOICES))
