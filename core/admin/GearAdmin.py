from core.admin.ViewableAdmin import ViewableModelAdmin
from core.views.GearViews import GearDetailView, GearViewList, GearTypeDetailView


class GearAdmin(ViewableModelAdmin):
    # Make all the data about a certification be shown in the list display
    list_display = ("name", "geartype", "status", "checked_out_to", "due_date")

    # Choose which fields appear on the side as filters
    list_filter = ('status', "geartype", "geartype__department")

    # Choose which fields can be searched for
    search_fields = ('name', 'rfid', "checked_out_to__first_name", "checked_out_to__last_name")

    fieldsets = (
        ('Gear Info', {
            'classes': ('wide',),
            'fields': ("rfid", "name", "geartype"),
        }),
        ('Checkout Info', {
            'classes': ('wide',),
            'fields': ("status", "checked_out_to", "due_date")
        })
    )

    list_view = GearViewList
    detail_view_class = GearDetailView


class GearTypeAdmin(ViewableModelAdmin):
    detail_view_class = GearTypeDetailView


