from core.models.GearModels import Gear, GearType
from core.models.TransactionModels import Transaction
from core.views.common import ModelDetailView
from core.views.ViewList import RestrictedViewList
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.utils import timezone
from uwccsystem.settings import WEB_BASE


class GearTypeDetailView(ModelDetailView):
    model = GearType


class GearDetailView(UserPassesTestMixin, ModelDetailView):

    model = Gear
    template_name = "admin/core/gear/gear_detail.html"

    raise_exception = True
    permission_denied_message = "You are not allowed to view this piece of gear!"

    def test_func(self):
        """Only show if user has this gear checked out or is allowed to view any gear"""
        user = self.request.user
        gear = self.get_object()
        can_view_any = user.has_permission("core.view_general_gear")
        checked_out_to_user = (
            gear.checked_out_to is not None and user == gear.checked_out_to
        )
        return can_view_any or checked_out_to_user

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **context):
        gear = self.get_object()

        context["can_edit_gear"] = self.request.user.has_permission("core.change_gear")

        context["department_url"] = reverse(
            "admin:core_department_detail", kwargs={"pk": gear.geartype.department.pk}
        )
        context["geartype_url"] = reverse(
            "admin:core_geartype_detail", kwargs={"pk": gear.geartype.pk}
        )
        context["related_transactions"] = Transaction.objects.filter(
            gear=gear
        ).order_by("-timestamp")
        if gear.checked_out_to:
            context["checked_out_to_url"] = reverse(
                "admin:core_member_detail", kwargs={"pk": gear.checked_out_to.pk}
            )
        context['view_transactions'] = self.request.user.has_permission("core.view_all_transactions")
        return super(GearDetailView, self).get_context_data(**context)


class GearViewList(RestrictedViewList):
    def __init__(self, *args, **kwargs):
        super(GearViewList, self).__init__(*args, **kwargs)

        # If the person won't have the right to view gear generally, they will only see the gear checked out to them
        if not self.request.user.has_permission("core.view_general_gear"):
            self.title = "Gear checked out to you"

    def test_func(self):
        """Everyone can see the gear list, but for non-staffers it is the gear checked out to them"""
        return self.request.user.has_permission("core.view_gear")

    def can_view_all(self):
        """If a user isn't allowed to view all gear, only show the gear that is available"""
        return self.request.user.has_permission("core.view_all_gear")

    def set_restriction_filters(self):
        """Board should see all gear, staffers see active gear, members only see gear checked out to them"""
        if self.request.user.has_permission("core.view_all_gear"):
            self.restriction_filters = {}
        elif self.request.user.has_permission("core.view_general_gear"):
            self.restriction_filters["status__lte"] = 3
        else:
            self.restriction_filters[
                "checked_out_to_id__exact"
            ] = self.request.user.primary_key
