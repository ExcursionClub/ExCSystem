"""This file is intended to contain only the admin classes for models that do not require much admin functionality"""

from core.admin.ViewableAdmin import ViewableModelAdmin
from core.views.OtherModelViews import CertificationDetailView, DepartmentDetailView
from django.contrib.admin import ModelAdmin


class CertificationAdmin(ViewableModelAdmin):

    # Make all the data about a certification be shown in the list display
    list_display = ("title", "requirements")
    detail_view_class = CertificationDetailView


class DepartmentAdmin(ViewableModelAdmin):

    # Make all the data about a department be shown in the list display
    list_display = ("name", "description", "stl_names")
    detail_view_class = DepartmentDetailView


class AlreadyUploadedImageAdmin(ModelAdmin):

    list_display = ("name", "image_type", "sub_type", "upload_date")
