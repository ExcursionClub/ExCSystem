from django import forms

from core.models.DepartmentModels import Department
from core.models.GearModels import Gear


class HomeForm(forms.Form):
    rfid = forms.CharField(max_length=10)


FRUIT_CHOICES = [
    ('orange', 'Oranges'),
    ('cantaloupe', 'Cantaloupes'),
    ('mango', 'Mangoes'),
    ('honeydew', 'Honeydews'),
    ]


class DepartmentForm(forms.Form):
    DEPARTMENTS = [(department.name, department.name) for department in Department.objects.all()]
    department = forms.CharField(label='Select the department the gear is in',
                                     widget=forms.RadioSelect(choices=DEPARTMENTS))


class GearForm(forms.Form):
    GEAR = [(gear.name, gear.name) for gear in Gear.objects.all()]
    # TODO: Only show gear in selected department
    gear = forms.CharField(label='Select what you are retagging',
                           widget=forms.RadioSelect(choices=GEAR))
