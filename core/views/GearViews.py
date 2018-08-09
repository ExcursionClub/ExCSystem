from django.views.generic.detail import DetailView

from django.utils import timezone

from core.models.GearModels import Gear, GearType
from core.views.ViewList import RestrictedViewList
from core.views.common import ModelDetailView


class GearTypeDetailView(ModelDetailView):
    model = GearType


class GearDetailView(ModelDetailView):

    model = Gear


class GearViewList(RestrictedViewList):

    def test_func(self):
        """Users can see the gear list if the have that permission"""
        return self.request.user.has_permission("view_gear")

    def can_view_all(self):
        """If a user isn't allowed to view all gear, only show the gear that is available"""
        return self.request.user.has_permission("view_all_gear")

    def set_restriction_filters(self):
        """Staffers should be able to see active gear, members should only see available gear"""
        if self.request.user.is_staffer:
            self.restriction_filters["status__lte"] = 3
        else:
            self.restriction_filters["status"] = 0
