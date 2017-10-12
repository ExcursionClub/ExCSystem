from django.contrib import admin


class GearAdmin(admin.ModelAdmin):
    # Make all the data about a certification be shown in the list display
    list_display = ("name", "department", "status", "checked_out_to")

    # Choose which fields appear on the side as filters
    list_filter = ('status', "department")

    # Choose which fields can be searched for
    search_fields = ('name', 'rfid',)# "checked_out_to")  # TODO: check if checked out to is reasonable thing to search

