import json

from collections import OrderedDict

from core.admin.ViewableAdmin import ViewableModelAdmin
from core.views.GearViews import GearDetailView, GearViewList, GearTypeDetailView
from core.forms.GearForms import GearChangeForm, GearAddFormStart


class GearAdmin(ViewableModelAdmin):
    # Make all the data about a certification be shown in the list display
    list_display = ("name", "status", "get_department", "checked_out_to", "due_date")

    # Choose which fields appear on the side as filters
    list_filter = ('status', "geartype__department", "geartype")

    # Choose which fields can be searched for
    search_fields = ('name', 'rfid', "checked_out_to__first_name", "checked_out_to__last_name")

    fieldsets = [
        ('Gear Info', {
            'classes': ('wide',),
            'fields': ("rfid", "geartype"),
        }),
        ('Checkout Info', {
            'classes': ('wide',),
            'fields': ("status", "checked_out_to", "due_date")
        }),
    ]

    form = GearChangeForm
    initial_add_form = GearAddFormStart
    finish_add_form = GearChangeForm  # Hijack gear change to finalize the addition process TODO: Might want dedicated

    list_view = GearViewList
    detail_view_class = GearDetailView

    def get_fieldsets(self, request, obj=None):
        """Add in the dynamic fields defined by geartype into the fieldsets (so django knows how to display them)"""
        fieldsets = super(GearAdmin, self).get_fieldsets(request, obj=obj)

        # Only get the extra fieldsets if we already have an object created
        if obj:
            fieldsets = fieldsets + [obj.get_extra_fieldset()]  # Using append gives multiple copies of the extra fields

        return tuple(fieldsets)
    
    def get_form(self, request, obj=None, **kwargs):
        """Manually insert the form fields for our dynamic fields into the admin form so the data can be edited"""

        # If an object was passed, then we are dealing with an object change situation, so all fields on one page
        if obj:
            # Load the basic form, including an empty (required) attributes
            new_attrs = OrderedDict()
            extended_form = type(self.form.__name__, (self.form,), new_attrs)
            extended_form.authorizer_rfid = request.user.rfid

            # Load all the fields that need to be added dynamically from the geartype
            gear_data = json.loads(obj.gear_data)
            extra_fields = obj.geartype.data_fields.all()

            # For each dynamic field, add it to declared fields and the fields list (returned here)
            for field in extra_fields:
                field_data = gear_data[field.name]
                form_field = field.get_field(**field_data)
                extended_form.declared_fields.update({field.name: form_field})
            return super(GearAdmin, self).get_form(request, obj=obj, form=extended_form, **kwargs)

        # If no obj was passed, assume we are creating a new object, so we split creation into two parts. The first part
        # is just the default creation page with the default fields, the second page (based on gear type) is handled in
        # one of the add response functions (see below)
        else:
            # Load the add form, including an empty (required) attributes
            new_attrs = OrderedDict()
            add_form = type(self.initial_add_form.__name__, (self.initial_add_form,), new_attrs)
            add_form.authorizer_rfid = request.user.rfid
            return super(GearAdmin, self).get_form(request, obj=None, form=add_form, **kwargs)


class GearTypeAdmin(ViewableModelAdmin):
    detail_view_class = GearTypeDetailView


