from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from functools import update_wrapper

from core.admin.ViewableAdmin import ViewableModelAdmin
from core.forms.MemberForms import MemberChangeForm, MemberCreationForm
from core.views.MemberViews import (MemberDetailView, MemberFinishView, MemberListView, )


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
            'fields': ('username', 'password1', 'password2', 'rfid'),
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
            'fields': ('rfid', 'groups',)
        })
    )

    search_fields = ('email', 'phone_number', 'first_name', 'last_name', 'rfid')
    ordering = ('first_name',)
    filter_horizontal = ()
    list_view = MemberListView
    detail_view = MemberDetailView

    def response_add(self, request, obj, post_url_continue=None):
        """Redirect to the detail page after saving the new member, unless we're adding another"""
        if '_addanother' not in request.POST and '_continue' not in request.POST:
            return HttpResponseRedirect(reverse("admin:core_member_detail", kwargs={'pk': obj.pk}))
        else:
            return super(MemberAdmin, self).response_add(request, obj, post_url_continue)


class StafferAdmin(ViewableModelAdmin):
    pass
