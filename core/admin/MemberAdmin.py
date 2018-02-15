from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import path
from functools import update_wrapper

from core.forms.MemberForms import MemberChangeForm, MemberCreationForm
from core.views.ViewList import ViewList
from core.views.MemberViews import MemberDetailView


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

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'rfid'),
        }),
    )
    exclude = ('date_joined', )

    search_fields = ('email', 'phone_number', 'first_name', 'last_name', 'rfid')
    ordering = ('first_name',)
    filter_horizontal = ()

    def get_changelist(self, request, **kwargs):
        return ViewList

    def get_urls(self):
        """Get all the urls admin related urls for member. Overridden here to add the detail view url"""

        # Using this wrapper to call the view allows us to check permissions
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        # Get all the urls automatically generated for a admin view of a model by django
        urls = super().get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        # Setup all the additional urls we want
        my_urls = [
            path('<int:pk>/detail/', wrap(MemberDetailView.as_view()), name='%s_%s_detail' % info),
        ]

        # Return all of our newly created urls along with all of the defaults
        return my_urls + urls
