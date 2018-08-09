import importlib
import json

from django.db import models
from .MemberModels import Member
from .DepartmentModels import Department
from .CertificationModels import Certification

from django.forms.widgets import TextInput, Textarea, NumberInput, CheckboxInput, Select
from core.forms.widgets import RFIDWidget

from django.forms.fields import CharField, ChoiceField, IntegerField, FloatField, BooleanField
from django.forms.models import ModelChoiceField
from core.forms.fields.RFIDField import RFIDField

from django.core import serializers
from django.apps import apps

# TODO: subclass Gear for all the different types of gear
# TODO: figure out how to "subclass" via the django admin, so a new type of gear could be added if necessary


class CustomDataField(models.Model):
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
    fields = {
        "rfid": RFIDField,
        "text": CharField,
        "string": CharField,
        "boolean": BooleanField,
        "int": IntegerField,
        "float": FloatField,
        "choice": ChoiceField,
        "reference": ModelChoiceField
    }

    name = models.CharField(max_length=30, unique=True)
    data_type = models.CharField(max_length=20, choices=data_types)
    suffix = models.CharField(max_length=10)

    def __str__(self):
        name = self.name
        return name.replace('_', ' ').title()

    def serialize_rfid(self, rfid, **kwargs):
        return {
            "initial": rfid,
        }

    def serialize_text(self, text, max_length=300, min_length=0, strip=True, **kwargs):
        return {
            "initial": text,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip
        }

    def serialize_string(self, string, max_length=50, min_length=0, strip=True, **kwargs):
        return {
            "initial": string,
            "max_length": max_length,
            "min_length": min_length,
            "strip": strip
        }

    def serialize_boolean(self, boolean, **kwargs):
        return {
            "initial": boolean,
        }

    def serialize_int(self, value, min_value=-100, max_value=100, **kwargs):
        return {
            "initial": value,
            "min_value": min_value,
            "max_value": max_value
        }

    def serialize_float(self, value, min_value=-1000, max_value=1000, **kwargs):
        return {
            "initial": value,
            "min_value": min_value,
            "max_value": max_value
        }

    def serialize_choice(self, value, choices=(("None", "No choices provided"),), **kwargs):
        return {
            "initial": value,
            "choices": choices
        }

    def serialize_reference(self, obj, object_type=None, selectable_objects=None, **kwargs):
        if object_type:
            kwargs['app_label'] = object_type._meta.app_label
            kwargs['model_name'] = object_type.__name__
        elif 'app_label' in kwargs.keys() and 'model_name' in kwargs.keys():
            module = importlib.import_module(f"{kwargs['app_label']}.models")
            object_type = getattr(module, kwargs['model_name'])

        if not selectable_objects:
            selectable_objects = object_type.objects.all()

        return {
            "initial": str(obj) if obj else None,
            "pk": obj.pk if obj else None,
            "app_label": kwargs['app_label'],
            "model_name": kwargs['model_name'],
            "selectable_objects": serializers.serialize("json", selectable_objects)
        }
    
    def get_reference_field(self, pk=None, app_label=None, model_name=None, selectable_objects=None, **init_data):
        object_type = apps.get_model(app_label, model_name)
        init_data["initial"] = object_type.objects.get(pk=pk)
        if selectable_objects:
            selectable_objects = serializers.deserialize('json', selectable_objects)
        return ModelChoiceField(selectable_objects, **init_data)

    def serialize(self, required=False, label="", initial=None, help_text="", **kwargs):
        """Execute the serialize function appropriate for the current data type"""
        serialize_function = getattr(self, f"serialize_{self.data_type}")
        serialized = serialize_function(initial, **kwargs)
        serialized["data_type"] = self.data_type
        serialized["name"] = self.name
        serialized["required"] = required
        serialized["label"] = label
        serialized["help_text"] = help_text
        return serialized

    def get_value(self, data_dict):
        """Returns the object currently stored by this field"""
        if self.data_type == "choice":
            selected = data_dict["initial"]
        elif self.data_type == "reference":
            obj_type = data_dict["object_type"]
            model = importlib.import_module(f"core.models.{obj_type}")
            return model.objects.get(pk=data_dict["pk"])
        else:
            return data_dict["initial"]

    def get_str(self, data_dict):
        """Get the string representation of the value of this field"""
        value = self.get_value(data_dict)

        # The string of choice should be the human readable version, not the actual value
        if value and self.data_type == 'choice':
            for choice in data_dict["choices"]:
                if choice[0] == value:
                    return choice[1]
            raise KeyError(f"Selected choice ({value}) not found for {self.name} field!")

        # If we got a value, connect it with the suffix to get the string representation
        elif value:
            return " ".join([str(value), self.suffix]).strip()
        else:
            return None

    def get_field(self, init_data, current=None):
        """Returns the appropriate FormField for the current data type"""
        # If a current field value is passed, set it as the initial value for the returned form field
        if current is not None:
            init_data['initial'] = current

        init_data['widget'] = self.widgets[self.data_type]

        # Only reference fields need special attention
        if self.data_type == 'reference':
            field = self.get_reference_field(**init_data)
        else:
            field = self.fields[self.data_type](**init_data)

        return field


class GearType(models.Model):

    name = models.CharField(max_length=30)

    #: The department to which this type of gear belongs (roughly corresponds to STL positions)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    #:
    data_fields = models.ManyToManyField(CustomDataField)

    def __str__(self):
        return self.name


class GearManager(models.Manager):

    def _create(self, rfid, gear_type, **gear_data):
        """
        Create a piece of gear that contains the basic data, and all additional data specified by the gear_type

        NOTE: THIS SHOULD ALWAYS BE CALLED THROUGH A TRANSACTION!
        """

        # Create a simple piece of gear without any extra gear data
        gear = Gear(
            rfid=rfid,
            status=0,
            geartype=gear_type
        )

        # Filter out any passed data that is not referenced by the gear type
        extra_fields = CustomDataField.objects.filter(geartype=gear_type)
        data_dict = {}
        for field in extra_fields:
            data_dict[field.name] = field.serialize(**gear_data[field.name])

        # Add in the additional data as a string before saving the piece of gear
        gear.gear_data = json.dumps(data_dict)
        gear.save()

        return gear

    def _add(self, rfid, name, gear_type, **gear_data):
        """
        Alias for gear creation


        NOTE: THIS SHOULD ALWAYS BE CALLED THROUGH A TRANSACTION!
        """
        return self.create(rfid, gear_type, name=name, **gear_data)


class Gear(models.Model):
    """
    The base model for a piece of gear
    """

    objects = GearManager()

    class Meta:
        verbose_name_plural = "Gear"

    rfid = models.CharField(max_length=10, unique=True)
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

    #: All the certifications that a member must posses to be allowed to check out this gear
    min_required_certs = models.ManyToManyField(Certification, verbose_name="Minimal Certifications Required for Rental")

    #: Who currently has this piece of gear. If null, then the gear is not checked out
    checked_out_to = models.ForeignKey(Member, null=True, on_delete=models.SET_NULL)

    #: The date at which this gear is due to be returned, null if not checked out
    due_date = models.DateField(null=True, default=None)

    geartype = models.ForeignKey(GearType, on_delete=models.CASCADE)

    gear_data = models.CharField(max_length=2000)

    # TODO: Add image of gear

    def __str__(self):
        return self.name

    def __getattr__(self, item):
        """
        Allows the values of CustomDataFields stored in GearType to be accessed as if they were attributes of Gear
        """

        gear_data = json.loads(self.__getattribute__('gear_data'))

        if item is None:
            return self
        elif item in gear_data.keys():
            gear_type = self.__getattribute__('geartype')
            field = gear_type.data_fields.get(name=item)
            return field.get_value(gear_data[item])
        else:
            raise AttributeError(f'No field {item} for {repr(self)}!')

    @property
    def name(self):
        """
        Auto-generate a name that can (semi-uniquely) identify this piece of gear

        Name will be in the form: <GearType> - <attr 1>, <attr 2>, etc...
        """

        # Get all custom data fields for this data_type, except those that contain a reference
        attr_fields = self.geartype.data_fields.exclude(data_type='reference')
        attributes = []
        gear_data = json.loads(self.gear_data)
        for field in attr_fields:
            string = field.get_str(gear_data[field.name])
            if string:
                attributes.append(str(string))

        if attributes:
            attr_string = ", ".join(attributes)
            name = f'{self.geartype.name} - {attr_string}'
        else:
            name = self.geartype.name

        return name

    def get_department(self):
        return self.geartype.department
    get_department.short_description = "Department"

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


