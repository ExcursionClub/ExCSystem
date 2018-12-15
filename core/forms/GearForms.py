import json

from core.forms.widgets import GearImageWidget
from core.models.FileModels import AlreadyUploadedImage
from core.models.GearModels import Gear
from core.models.TransactionModels import Transaction
from django.forms import ModelChoiceField, ModelForm, ValidationError


class GearChangeForm(ModelForm):

    class Meta:
        model = Gear
        fields = '__all__'

    authorizer_rfid = None
    existing_images = AlreadyUploadedImage.objects.filter(image_type="gear")
    image = ModelChoiceField(existing_images, widget=GearImageWidget)

    def __init__(self, *args, **kwargs):
        super(GearChangeForm, self).__init__(*args, **kwargs)

        # Make gear type non-editable. Necessary to avoid data corruption
        self.fields["geartype"].disabled = True

    def clean_gear_data(self):
        """Compile the data from all the custom fields to be saved into gear_data"""
        # TODO: Fix this
        gear_data_dict = {}
        original_gear_data = json.loads(self.instance.gear_data)
        for name in self.declared_fields.keys():
            if name == "image":
                continue
            value = self.cleaned_data[name]
            field_data = original_gear_data[name]
            field_data["initial"] = value
            gear_data_dict[name] = field_data

        return json.dumps(gear_data_dict)

    def save(self, commit=True):
        """Save using the Transactions instead of using the gear object directly"""

        # Django really wants to call this function, even though it does nothing for gear
        self.save_m2m = self._save_m2m

        self.cleaned_data['gear_data'] = self.clean_gear_data()
        gear_rfid = self.cleaned_data.pop('rfid')
        change_data = self.cleaned_data
        transaction, gear = Transaction.objects.override(
            self.authorizer_rfid,
            gear_rfid,
            **change_data
        )
        return gear


class GearAddForm(ModelForm):
    """The form used to set the initial data about a new piece of gear"""

    class Meta:
        model = Gear
        fields = '__all__'

    authorizer_rfid = None
    # TODO: Get all images as objects from S3
    existing_images = AlreadyUploadedImage.objects.filter(image_type="gear")

    def __init__(self, *args, **kwargs):
        super(GearAddForm, self).__init__(*args, **kwargs)
        # Don't disable geartype, this is the only time it should be editable
        # Set the default status to be in stock
        self.fields["status"].initial = 0

    def build_gear_data(self):
        """During the initial creation of the gear, the gear data JSON must be created."""
        geartype = self.instance.geartype
        return geartype.build_empty_data()

    def clean_rfid(self):
        cleaned_rfid = self.cleaned_data.get('rfid')

        if len(cleaned_rfid) != 10:
            raise ValidationError('The rfid has to be 10 digits')
        try:
            int(cleaned_rfid)
        except ValueError:
            raise ValidationError("The rfid can only contain digits")
        # TODO: Validate that the rfid isn't already in use
        return cleaned_rfid

    def save(self, commit=True):
        """Save this new instance, making sure to use the Transaction method"""

        # Django really wants to call this function, even though it does nothing for gear
        self.save_m2m = self._save_m2m

        transaction, gear = Transaction.objects.add_gear(
            self.authorizer_rfid,
            self.cleaned_data['rfid'],
            self.cleaned_data['geartype'],
            self.cleaned_data['image'],
            **self.build_gear_data(),
        )
        return gear
