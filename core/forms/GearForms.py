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

