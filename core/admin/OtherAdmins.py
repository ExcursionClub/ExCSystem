"""This file is intended to contain only the admin classes for models that do not require much admin functionality"""

from django.contrib import admin


class CertificationAdmin(admin.ModelAdmin):

    # Make all the data about a certification be shown in the list display
    list_display = ("title", "requirements")


class DepartmentAdmin(admin.ModelAdmin):

    # Make all the data about a department be shown in the list display
    list_display = ("name", "description", "stl_names")


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("type", "timestamp", "gear", "member", "authorizer", "comments")
    list_filter = ("type", )
    search_fields = ("gear__name", "member__first_name", "member__last_name",
                     "authorizer__first_name", "authorizer__last_name")
