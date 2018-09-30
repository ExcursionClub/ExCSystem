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

    def __init__(self, *args, **kwargs):
        super(GearViewList, self).__init__(*args, **kwargs)

        # If the person won't have the right to view gear generally, they will only see the gear checked out to them
        if not self.request.user.has_permission('view_general_gear'):
            self.title = 'Gear checked out to you'

    def test_func(self):
        """Everyone can see the gear list, but for non-staffers it is the gear checked out to them"""
        return self.request.user.has_permission('view_gear')

    def can_view_all(self):
        """If a user isn't allowed to view all gear, only show the gear that is available"""
        return self.request.user.has_permission("view_all_gear")

    def set_restriction_filters(self):
        """Staffers should be able to see active gear, members should only see available gear"""
        if self.request.user.has_permission('view_general_gear'):
            self.restriction_filters["status__lte"] = 3
        else:
            self.restriction_filters["checked_out_to_id__exact"] = self.request.user.primary_key
