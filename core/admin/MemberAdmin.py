from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.forms.MemberForms import MemberChangeForm, MemberCreationForm
from core.views.ViewList import ViewList


# Replace the option to create users with the option to create members
class MemberAdmin(BaseUserAdmin):
    # The forms to add and change member instances
    form = MemberChangeForm
    add_form = MemberCreationForm

    # The fields to be used in displaying the Member model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('get_full_name', 'email', 'phone_number', 'date_joined', 'date_expires', 'status')
    list_filter = ('status',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number',)}),
        ('Club info', {'fields': ('rfid', 'picture')}),
        ('Permissions', {'fields': ('status',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. MemberAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'rfid', 'password1', 'password2',)}
        ),
    )
    search_fields = ('email', 'phone_number', 'first_name', 'last_name', 'rfid')
    ordering = ('first_name',)
    filter_horizontal = ()

    def get_changelist(self, request, **kwargs):
        return ViewList
