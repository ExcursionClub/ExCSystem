import json

from django.forms import ModelForm

from core.models.GearModels import Gear


class GearChangeForm(ModelForm):

    class Meta:
        model = Gear
        fields = '__all__'

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
        self.instance.gear_data = self.clean_gear_data()
        super(GearChangeForm, self).save(commit=commit)
        return self.instance

