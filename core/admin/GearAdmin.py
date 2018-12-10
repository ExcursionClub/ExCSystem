import json
from collections import OrderedDict

from core.admin.ViewableAdmin import ViewableModelAdmin
from core.forms.GearForms import GearAddForm, GearChangeForm
from core.views.GearViews import GearDetailView, GearTypeDetailView, GearViewList
from django.contrib.admin import ModelAdmin
from django.contrib.admin.utils import quote
from django.http import HttpResponseRedirect
from django.urls import reverse


class GearAdmin(ViewableModelAdmin):
    # Make all the data about a certification be shown in the list display
    list_display = ("name", "status", "get_department", "checked_out_to", "due_date")

    # Choose which fields appear on the side as filters
    list_filter = ('status', "geartype__department", "geartype")

    # Choose which fields can be searched for
    search_fields = ('geartype__name', 'gear_data', 'rfid', 'checked_out_to__first_name', 'checked_out_to__last_name')

    fieldsets = [
        ('Gear Info', {
            'classes': ('wide',),
            'fields': ("rfid", "geartype", "image"),
        }),
        ('Checkout Info', {
            'classes': ('wide',),
            'fields': ("status", "checked_out_to", "due_date")
        }),
    ]

    form = GearChangeForm
    add_form = GearAddForm

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
            add_form = type(self.add_form.__name__, (self.add_form,), new_attrs)
            add_form.authorizer_rfid = request.user.rfid
            return super(GearAdmin, self).get_form(request, obj=None, form=add_form, **kwargs)

    def response_add(self, request, obj, post_url_continue=None):
        """After adding a new piece of gear, always go to the 'change' page to finish filling out gear data"""
        change_url = reverse(
            f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
            args=(quote(obj.pk),),
            current_app=self.admin_site.name,)
        return HttpResponseRedirect(change_url)


class GearTypeAdmin(ViewableModelAdmin):
    """
    Admin class to make gear types viewable

    Since gear types have on_delete set to CASCADE, if a gear type has been used on a piece of gear (and is therefore
    referenced in transaction), no-one will be able to delete that gear type, since deleting Transactions is explicitly
    forbidden for all users, including admin
    """
    detail_view_class = GearTypeDetailView

    def has_change_permission(self, request, obj=None):
        """No one should have permissions to change gear types, it'll guaranteed destroy data"""
        return False


class CustomDataFieldAdmin(ModelAdmin):
    """Forbid anyone from changing CustomDataFields"""

    def has_change_permission(self, request, obj=None):
        return False
