from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import DetailView

from core.models.CertificationModels import Certification
from core.models.DepartmentModels import Department


class CertificationDetailView(UserPassesTestMixin, DetailView):

    model = Certification
    template_name = "admin/core/detail.html"

    raise_exception = True
    permission_denied_message = "You are not allowed to view the Certifications!"

    def test_func(self):
        return self.request.user.has_permission("view_certification")

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)


class DepartmentDetailView(UserPassesTestMixin, DetailView):
    model = Department
    template_name = "admin/core/detail.html"

    raise_exception = True
    permission_denied_message = "You are not allowed to view the Gear departments!"

    def test_func(self):
        return self.request.user.has_permission("view_department")

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)