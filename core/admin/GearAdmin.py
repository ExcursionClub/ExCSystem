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

