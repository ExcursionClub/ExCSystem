import json

from core.forms.fields.RFIDField import RFIDField
from core.forms.widgets import ExistingImageWidget
from core.models.fields.PrimaryKeyField import PrimaryKeyField
from core.models.FileModels import AlreadyUploadedImage
from django.db import models
from django.forms.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    FloatField,
    IntegerField,
)
from django.forms.widgets import CheckboxInput, NumberInput, Select, Textarea, TextInput
from django.urls import reverse
from datetime import date

from .CertificationModels import Certification
from .DepartmentModels import Department
from .MemberModels import Member
from uwccsystem.settings import GEAR_EXPIRE_TIME

class CustomDataField(models.Model):
    data_types = (
        ("rfid", "10 digit RFID"),
        ("text", "String of any length"),
        ("string", "Short string of up to 50 characters"),
        ("boolean", "True/False value"),
        ("int", "Integer value"),
        ("float", "Float value"),
        ("choice", "Short string selectable from a list"),
    )
    widgets = {
        "rfid": TextInput,
        "text": Textarea,
        "string": TextInput,
        "boolean": CheckboxInput,
        "int": NumberInput,
        "float": NumberInput,
        "choice": Select,
    }
    fields = {
        "rfid": RFIDField,
        "text": CharField,
        "string": CharField,
        "boolean": BooleanField,
        "int": IntegerField,
        "float": FloatField,
        "choice": ChoiceField,
    }

    name = models.CharField(max_length=30, unique=True)
    data_type = models.CharField(max_length=20, choices=data_types)
    suffix = models.CharField(max_length=10, default="", blank=True)
    required = models.BooleanField(default=False)
    label = models.CharField(max_length=30, default="")
    help_text = models.CharField(max_length=200, default="", blank=True)

    choices = models.TextField(
        max_length=1000,
        default="None; No choices provided\nNope; Also not a choice",
        help_text="Must use this format to define choices!\n"
        "Each choice must be on it's own line, and consist of a short name (used internally), and a "
        "description (seen by the user). Name description pairs must be separated by a semicolon, and no "
        "semicolons are allowed in either the name or the description",
        blank=True,
    )

    def __str__(self):
        name = self.name
        return name.replace("_", " ").title()

    def serialize_rfid(self, rfid, **kwargs):
        return {"initial": rfid}

    def serialize_text(self, text, max_length=300, min_length=0, strip=True, **kwargs):
        return {
            "initial": text,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip,
        }

    def serialize_string(
        self, string, max_length=50, min_length=0, strip=True, **kwargs
    ):
        return {
            "initial": string,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip,
        }

    def serialize_boolean(self, boolean, required=False, **kwargs):
        return {"initial": boolean, "required": required}

    def serialize_int(self, value, min_value=-100, max_value=100, **kwargs):
        return {"initial": value, "min_value": min_value, "max_value": max_value}

    def serialize_float(self, value, min_value=-1000, max_value=1000, **kwargs):
        return {"initial": value, "min_value": min_value, "max_value": max_value}

    def serialize_choice(self, value, choices=None, **kwargs):
        # If a set of choices is not given, then try to parse out the choices from the choice field
        if not choices:
            choices = []
            choice_list = self.choices.split("\n")
            for choice_pair in choice_list:
                choice = choice_pair.split(";")
                choices.append((choice[0].strip(), choice[1].strip()))

        return {"initial": value, "choices": tuple(choices)}

    def serialize(
        self, required=None, label=None, initial=None, help_text=None, **kwargs
    ):
        """Execute the serialize function appropriate for the current data type"""
        serialize_function = getattr(self, f"serialize_{self.data_type}")
        serialized = serialize_function(initial, **kwargs)
        serialized["data_type"] = self.data_type
        serialized["name"] = self.name
        serialized["required"] = required if required else self.required
        serialized["label"] = label if label else self.label
        serialized["help_text"] = help_text if help_text else self.help_text
        return serialized

    def get_value(self, data_dict):
        """Returns the object currently stored by this field"""
        return data_dict["initial"]

    def get_str(self, data_dict):
        """Get the string representation of the value of this field"""
        value = self.get_value(data_dict)

        # The string of choice should be the human readable version, not the actual value
        if value and self.data_type == "choice":
            for choice in data_dict["choices"]:
                if choice[0] == value:
                    return choice[1]
            raise KeyError(
                f"Selected choice ({value}) not found for {self.name} field!"
            )

        # If we got a value, connect it with the suffix to get the string representation
        elif value:
            return " ".join([str(value), self.suffix]).strip()
        else:
            return None

    def get_field(self, current=None, **init_data):
        """Returns the appropriate FormField for the current data type"""

        # If a current field value is passed, set it as the initial value for the returned form field
        if current is not None:
            init_data["initial"] = current

        # Remove data that is used for reference in JSON format, but would interfere with form field instantiation
        init_data.pop("name")
        init_data.pop("data_type")

        # Make sure that the default widget for this data type is used
        init_data["widget"] = self.widgets[self.data_type]

        field = self.fields[self.data_type](**init_data)

        return field


class GearType(models.Model):

    name = models.CharField(max_length=30)

    #: The department to which this type of gear belongs (roughly corresponds to STL positions)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    #: All the certifications that a member must posses to be allowed to check out this gear
    min_required_certs = models.ManyToManyField(
        Certification,
        verbose_name="Minimal Certifications Required for Rental",
        blank=True,
        default=None,
    )

    #:
    data_fields = models.ManyToManyField(CustomDataField)

    def __str__(self):
        return self.name

    def requires_certs(self):
        return True if self.min_required_certs else False

    def get_field_names(self):
        """Return a list of the names of fields included in this gear type"""
        field_names = []
        for field in self.data_fields.all():
            field_names.append(field.name)
        return field_names

    def build_empty_data(self):
        """Construct a empty gear data dict that contains no gear data"""
        data_dict = {}
        for field in self.data_fields.all():
            data_dict[field.name] = field.serialize()
        return data_dict


class GearManager(models.Manager):
    def _create(self, rfid, geartype, image, **gear_data):
        """
        Create a piece of gear that contains the basic data, and all additional data specified by the geartype

        NOTE: THIS SHOULD ALWAYS BE CALLED THROUGH A TRANSACTION!
        """

        # Create a simple piece of gear without any extra gear data
        gear = Gear(rfid=rfid, status=0, geartype=geartype, image=image)

        # Filter out any passed data that is not referenced by the gear type
        extra_fields = CustomDataField.objects.filter(geartype=geartype)
        data_dict = {}
        for field in extra_fields:
            data_dict[field.name] = field.serialize(**gear_data[field.name])

        # Add in the additional data as a string before saving the piece of gear
        gear.gear_data = json.dumps(data_dict)
        gear.save()

        return gear

    def _add(self, rfid, name, geartype, **gear_data):
        """
        Alias for gear creation


        NOTE: THIS SHOULD ALWAYS BE CALLED THROUGH A TRANSACTION!
        """
        return self.create(rfid, geartype, name=name, **gear_data)


class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    objects = GearManager()

    class Meta:
        verbose_name_plural = "Gear"

    primary_key = PrimaryKeyField()
    rfid = models.CharField(max_length=10, unique=True)
    image = models.ForeignKey(AlreadyUploadedImage, on_delete=models.CASCADE)
    status_choices = [
        (0, "In Stock"),  # Ready and available in the gear sheds, waiting to be used
        (
            1,
            "Checked Out",
        ),  # Somebody has it right now, but it should soon be available again
        (
            2,
            "Broken",
        ),  # It is broken to the point it should not be checked out, waiting for repair
        (
            3,
            "Missing",
        ),  # Has been checked out for a while, time to yell at a member to give it back
        (
            4,
            "Dormant",
        ),  # Missing for very long time: assume it has been lost until found
        (5, "Removed"),  # It is gone, dead and never coming back. Always set manually
    ]
    #: The status determines what transactions the gear can participate in and where it is visible
    status = models.IntegerField(choices=status_choices)

    #: Who currently has this piece of gear. If null, then the gear is not checked out
    checked_out_to = models.ForeignKey(
        Member, blank=True, null=True, on_delete=models.SET_NULL
    )

    #: The date at which this gear is due to be returned, null if not checked out
    due_date = models.DateField(blank=True, null=True, default=None)

    geartype = models.ForeignKey(GearType, on_delete=models.CASCADE)

    gear_data = models.CharField(max_length=2000)

    def __str__(self):
        return self.name

    def __getattr__(self, item):
        """
        Allows the values of CustomDataFields stored in GearType to be accessed as if they were attributes of Gear
        """

        gear_data = json.loads(self.__getattribute__("gear_data"))

        if item is None:
            return self
        elif item in gear_data.keys():
            geartype = self.__getattribute__("geartype")
            field = geartype.data_fields.get(name=item)
            return field.get_value(gear_data[item])
        else:
            raise AttributeError(f"No attribute {item} for {repr(self)}!")

    def get_display_gear_data(self):
        """Return the gear data as a simple dict of field_name, field_value"""
        simple_data = {}
        attr_fields = self.geartype.data_fields.all()
        gear_data = json.loads(self.gear_data)
        for field in attr_fields:
            simple_data[field.name] = field.get_str(gear_data[field.name])
        return simple_data

    @property
    def edit_gear_url(self):
        return reverse("admin:core_gear_change", kwargs={"object_id": self.pk})

    @property
    def view_gear_url(self):
        return reverse("admin:core_gear_detail", kwargs={"pk": self.pk})

    def get_extra_fieldset(self, name="Additional Data", classes=("wide",)):
        """Get a fieldset that contains data on how to represent the extra data fields contained in geartype"""
        fieldset = (
            name,
            {"classes": classes, "fields": self.geartype.get_field_names()},
        )
        return fieldset

    def get_status(self):
        return self.status_choices[self.status][1]

    @property
    def image_url(self):
        if self.image and hasattr(self.image, "url"):
            return self.image.url

    @property
    def name(self):
        """
        Auto-generate a name that can (semi-uniquely) identify this piece of gear

        Name will be in the form: <GearType> - <attr 1>, <attr 2>, etc...
        """

        # Get all custom data fields for this data_type, except those that contain a rfid
        attr_fields = self.geartype.data_fields.exclude(data_type="rfid")
        attributes = []
        gear_data = json.loads(self.gear_data)
        for field in attr_fields:
            string = field.get_str(gear_data[field.name])
            if string:
                attributes.append(str(string))

        if attributes:
            attr_string = ", ".join(attributes)
            name = f"{self.geartype.name} - {attr_string}"
        else:
            name = self.geartype.name

        return name

    def get_department(self):
        return self.geartype.department

    get_department.short_description = "Department"

    def is_available(self):
        """Returns True if the gear is available for renting"""
        return self.status == 0

    def is_rented_out(self):
        return self.status in [1, 3, 4]

    def is_active(self):
        """Returns True if the gear is actively in circulation (ie could be checked out in a few days)"""
        if self.status <= 1:
            return True
        else:
            return False

    def is_existent(self):
        """Returns True if the gear has not been removed or lost"""
        if self.status <= 3:
            return True
        else:
            return False
