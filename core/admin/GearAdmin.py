from django.contrib import admin
from django.views.generic import RedirectView
from functools import update_wrapper
# from django.urls import path

from core.views.GearViews import GearDetailView
from core.views.ViewList import ViewList


class GearAdmin(admin.ModelAdmin):
    # Make all the data about a certification be shown in the list display
    list_display = ("name", "department", "status", "checked_out_to", "due_date")

    # Choose which fields appear on the side as filters
    list_filter = ('status', "department")

    # Choose which fields can be searched for
    search_fields = ('name', 'rfid', "checked_out_to__first_name", "checked_out_to__last_name")

    def get_changelist(self, request, **kwargs):
        return ViewList

    def get_urls(self):
        """
        Adds the detail view to the urlpatterns, in addition to what the overwritten function does
        """
        from django.urls import path

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            path('', wrap(self.changelist_view), name='%s_%s_changelist' % info),
            path('add/', wrap(self.add_view), name='%s_%s_add' % info),
            path('autocomplete/', wrap(self.autocomplete_view), name='%s_%s_autocomplete' % info),
            path('<path:object_id>/change/', wrap(self.change_view), name='%s_%s_change' % info),
            path('<path:object_id>/history/', wrap(self.history_view), name='%s_%s_history' % info),
            path('<path:object_id>/delete/', wrap(self.delete_view), name='%s_%s_delete' % info),

            # Adding this with this name allows ViewList to automatically link to the view page
            path('<int:pk>/detail/', wrap(GearDetailView.as_view()), name='%s_%s_detail' % info),

        ]

        print(self.list_display_links)
        return urlpatterns
