from django.views.generic.detail import DetailView

from django.utils import timezone

from core.models.GearModels import Gear
from core.views.ViewList import RestrictedViewList

class GearDetailView(DetailView):

    model = Gear

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['opts'] = self.model._meta
        context['app_label'] = self.model._meta.app_label
        context['change'] = False
        context['is_popup'] = False
        context['add'] = False
        context['save_as'] = False
        context['has_delete_permission'] = False
        context['has_change_permission'] = False
        context['has_add_permission'] = False
        return context


class GearViewList(RestrictedViewList):

    def test_func(self):
        """Users can see the gear list if the have that permission"""
        return self.request.user.has_permission("view_gear")

    def can_view_all(self):
        """If a user isn't allowed to view all gear, only show the gear that is available"""

        if self.request.user.is_staffer:
            self.restriction_filters["status__lte"] = 3
        else:
            self.restriction_filters["status"] = 0

        return self.request.user.has_permission("view_all_gear")

