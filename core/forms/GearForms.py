import json

from django.forms import ModelForm

from core.models.GearModels import Gear
from core.models.TransactionModels import Transaction


class GearChangeForm(ModelForm):

    class Meta:
        model = Gear
        fields = '__all__'
    authorizer_rfid = None

    def __init__(self, *args, **kwargs):
        super(GearChangeForm, self).__init__(*args, **kwargs)

        # Make gear type non-editable. Necessary to avoid data corruption
        self.fields["geartype"].disabled = True

    def clean_gear_data(self):
        """Compile the data from all the custom fields to be saved into gear_data"""
        gear_data_dict = {}
        original_gear_data = json.loads(self.instance.gear_data)
        for name in self.declared_fields.keys():
            value = self.cleaned_data[name]
            field_data = original_gear_data[name]
            field_data["initial"] = value
            gear_data_dict[name] = field_data

        return json.dumps(gear_data_dict)

    def save(self, commit=True):
        self.cleaned_data['gear_data'] = self.clean_gear_data()
        gear_rfid = self.cleaned_data.pop('rfid')
        change_data = self.cleaned_data
        transaction, gear = Transaction.objects.override(
            self.authorizer_rfid,
            gear_rfid,
            self.cleaned_data
        )
        return gear


class GearAddFormStart(ModelForm):
    """The form used to set the initial data about a new piece of gear"""

    class Meta:
        model = Gear
        fields = '__all__'
    authorizer_rfid = None

    def __init__(self, *args, **kwargs):
        super(GearAddFormStart, self).__init__(*args, **kwargs)
        # Don't disable geartype, this is the only time it should be editable
        # Set the default status to be in stock
        self.fields["status"].initial = 0

    def clean_gear_data(self):
        """During the initial creation of the gear, the gear data JSON must be created."""
        gear_data_dict = {}
        return json.dumps(gear_data_dict)

    def save(self, commit=True):
        """Save this new instance, making sure to use the Transaction method"""
        Transaction.objects.add_gear(
            self.authorizer_rfid,
            self.cleaned_data['rfid'],
            self.cleaned_data['geartype'],
            **self.cleaned_data['gear_data']
        )