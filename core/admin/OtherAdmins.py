"""This file is intended to contain only the admin classes for models that do not require much admin functionality"""

from django.contrib import admin
from core.admin.ViewableAdmin import ViewableModelAdmin


class CertificationAdmin(ViewableModelAdmin):

    # Make all the data about a certification be shown in the list display
    list_display = ("title", "requirements")


class DepartmentAdmin(ViewableModelAdmin):

    # Make all the data about a department be shown in the list display
    list_display = ("name", "description", "stl_names")









