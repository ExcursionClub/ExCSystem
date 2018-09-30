from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from functools import update_wrapper

from core.admin.ViewableAdmin import ViewableModelAdmin
from core.forms.MemberForms import MemberChangeForm, MemberCreationForm
from core.views.MemberViews import (MemberDetailView, MemberFinishView, MemberListView, StafferDetailView, )


# Replace the option to create users with the option to create members
class MemberAdmin(ViewableModelAdmin, BaseUserAdmin):
    # The forms to add and change member instances
    form = MemberChangeForm
    add_form = MemberCreationForm

    # The fields to be used in displaying the Member model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('get_full_name', 'email', 'phone_number', 'date_joined', 'date_expires', 'group')
    list_filter = ('group',)

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Staff Use Only', {
            'classes': ('wide',),
            'fields': ('membership', 'rfid'),
        }),
    )
    fieldsets = (
        ('Contact Info', {
            'classes': ('wide',),
            'fields': ('email', 'phone_number',),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'picture')
        }),
        ('Club  Info', {
            'classes': ('wide',),
            'fields': ('rfid', 'group', 'certifications')
        })
    )
    editable_profile_fieldsets = (
        ('Profile Info', {
            'classes': ('wide',),
            'fields': ('email', 'phone_number', 'first_name', 'last_name')
        }),
    )
    search_fields = ('email', 'phone_number', 'first_name', 'last_name', 'rfid')
    ordering = ('first_name',)
    filter_horizontal = ()
    list_view = MemberListView
    detail_view_class = MemberDetailView

    def get_urls(self):
        """Get all the urls admin related urls for member. Overridden here to add the detail view url"""

        # Get all the urls automatically generated for a admin view of a model by django
        urls = super().get_urls()

        # Setup all the additional member finish url
        my_urls = [
            path('<int:pk>/finish/', self.wrap(MemberFinishView.as_view()), name='core_member_finish')
        ]

        # Return all of our newly created urls along with all of the defaults
        return my_urls + urls

    # Using this wrapper to call the view allows us to check permissions
    def wrap(self, view):
        def wrapper(*args, **kwargs):
            return self.admin_site.admin_view(view)(*args, **kwargs)

        wrapper.model_admin = self
        return update_wrapper(wrapper, view)

    def response_add(self, request, obj, post_url_continue=None):
        """Redirect to the detail page after saving the new member, unless we're adding another"""
        if '_addanother' not in request.POST and '_continue' not in request.POST:
            return HttpResponseRedirect(reverse("admin:core_member_detail", kwargs={'pk': obj.pk}))
        else:
            return super(MemberAdmin, self).response_add(request, obj, post_url_continue)

    @staticmethod
    def can_edit_profile(request, member_id):
        """Returns true if the current user is allowed to edit the member's profile data"""
        current_user = request.user
        is_self = current_user.primary_key == member_id
        return is_self or current_user.has_permission("change_member")
    
    @staticmethod
    def can_edit_all_data(request):
        return request.user.has_permission("change_member")

    def has_view_or_change_permission(self, request, obj=None):
        return self.has_change_permission(request, obj=obj) or self.has_view_permission(request, obj=obj)

    def has_change_permission(self, request, obj=None):
        if obj and obj._meta.model_name == 'member':
            return self.can_edit_profile(request, obj.primary_key)
        else:
            super(MemberAdmin, self).has_change_permission(request, obj=obj)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Determine which profile edit page should be seen by the current user"""
        if request.method == 'POST' and not self.can_edit_all_data(request):
            # TODO: make sure you can't pass any fields that you don't have permission to access
            # I think this gets handled by the form itself: it will ignore any data it did not generate form fields for
            pass
        
        return super(MemberAdmin, self).change_view(request, object_id, form_url=form_url, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        """Modify the changeform if the current user should only be able to edit profile data"""

        can_edit_all_data = self.can_edit_all_data(request)
        can_edit_profile = self.can_edit_profile(request, obj.primary_key)

        if can_edit_all_data:
            # If the user is allowed to edit all the data, then the default changeform works just fine
            return self.fieldsets
        elif can_edit_profile:
            # If the user can edit profile but not all data, then limit the displayed fields to profile data fields
            return self.editable_profile_fieldsets
        else:
            raise PermissionDenied


class StafferAdmin(ViewableModelAdmin):

    detail_view_class = StafferDetailView
