from django.db import models
from .MemberModels import Member
from .DepartmentModels import Department
from .CertificationModels import Certification

from django.forms.widgets import TextInput, Textarea, NumberInput, CheckboxInput, Select
from core.forms.widgets import RFIDWidget

from django.core import serializers

# TODO: subclass Gear for all the different types of gear
# TODO: figure out how to "subclass" via the django admin, so a new type of gear could be added if necessary


class CustomDataField:
    data_types = (
        ("rfid", "10 digit RFID"),
        ("text", "String of any length"),
        ("string", "Short string of up to 50 characters"),
        ("boolean", "True/False value"),
        ("int", "Integer value"),
        ("float", "Float value"),
        ("choice", "Short string selectable from a list"),
        ("reference", "Object name linked to the object")
    )
    widgets = {
        "rfid": RFIDWidget,
        "text": Textarea,
        "string": TextInput,
        "boolean": CheckboxInput,
        "int": NumberInput,
        "float": NumberInput,
        "choice": Select,
        "reference": Select
    }

    name = models.CharField(max_length=30)
    data_type = models.CharField(max_length=20, choices=data_types)

    def serialize_rfid(self, rfid, ):
        return {
            "value": rfid,
        }

    def serialize_text(self, text, max_length=300, min_length=0, strip=True):
        return {
            "value": text,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip
        }

    def serialize_string(self, string, max_length=50, min_length=0, strip=True):
        return {
            "value": string,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip
        }

    def serialize_boolean(self, boolean):
        return {
            "value": boolean,
        }

    def serialize_int(self, value, min_value=-100, max_value=100):
        return {
            "value": value,
            "min_value": min_value,
            "max_value": max_value
        }

    def serialize_float(self, value, min_value=-1000, max_value=1000):
        return {
            "value": value,
            "min_value": min_value,
            "max_value": max_value
        }

    def serialize_choice(self, value, choices=(("None", "No choices provided"),)):
        return {
            "value": value,
            "choices": choices
        }

    def serialize_reference(self, obj, object_type=None, selectable_objects=None):
        if object_type is None:
            raise ValueError("Object Type must be specified when serializing an object reference")
        if selectable_objects:
            selectable_objects = object_type.objects.all()
        return {
            "value": obj.pk,
            "object_type": str(object_type),
            "selectable_objects": serializers.serialize("json", selectable_objects)
        }

    def serialize(self, data, required=False, label="", initial=None, help_text="", **kwargs):
        """Execute the serialize function appropriate for the current data type"""
        serialize_function = getattr(self, f"serialize_{self.data_type}")
        serialized = serialize_function(data, **kwargs)
        serialized["data_type"] = self.data_type
        serialized["name"] = self.name
        serialized["required"] = required
        serialized["label"] = label
        serialized["initial"] = initial
        serialized["help_text"] = help_text

    def get_value(self, data):
        """Returns the object currently stored by this field"""
        serialize_function = getattr(self, f"deserialize_{self.data_type}")
        return serialize_function(data)

    def get_field(self, data):
        """Returns the appropriate FormField for the current data type"""


class GearType:
    #: The department to which this type of gear belongs (roughly corresponds to STL positions)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    #:
    data_fields = models.ManyToManyField(CustomDataField)


class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    class Meta:
        verbose_name_plural = "Gear"

    rfid = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=50)
    status_choices = [
        (0, "In Stock"),        # Ready and available in the gear sheds, waiting to be used
        (1, "Checked Out"),     # Somebody has it right now, but it should soon be available again
        (2, "Broken"),          # It is broken to the point it should not be checked out, waiting for repair
        (3, "Missing"),         # Has been checked out for a while, time to yell at a member to give it back
        (4, "Dormant"),         # Missing for very long time: assume it has been lost until found
        (5, "Removed"),         # It is gone, dead and never coming back. Always set manually
    ]
    #: The status determines what transactions the gear can participate in and where it is visible
    status = models.IntegerField(choices=status_choices)

    #: The department to which this gear belongs (roughly corresponds to STL positions)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    #: All the certifications that a member must posses to be allowed to check out this gear
    min_required_certs = models.ManyToManyField(Certification, verbose_name="Minimal Certifications Required for Rental")

    #: Who currently has this piece of gear. If null, then the gear is not checked out
    checked_out_to = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL)

    #: The date at which this gear is due to be returned, null if not checked out
    due_date = models.DateField(null=True, default=None)

    gear_type = models.ForeignKey(GearType, on_delete=models.CASCADE)

    # TODO: Add image of gear

    def __str__(self):
        return self.name

    def is_available(self):
        """Returns True if the gear is available for renting"""
        if self.status == 0:
            return True
        else:
            return False

    def is_rented_out(self):
        return True if self.status == 1 else False

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


