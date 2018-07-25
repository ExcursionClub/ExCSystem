from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin

from ExCSystem.settings.base import WEB_BASE

from core.views.ViewList import RestrictedViewList
from core.models.MemberModels import Member
from core.forms.MemberForms import (MemberFinishForm, MemberUpdateContactForm, MemberChangeCertsForm,
                                    MemberChangeRFIDForm, MemberChangeGroupsForm, StafferDataForm)


def get_default_context(obj, context):
    """Convenience function for getting the default context data of a member"""
    context['now'] = timezone.now()
    context['opts'] = obj.model._meta
    context['app_label'] = obj.model._meta.app_label
    context['change'] = False
    context['is_popup'] = False
    context['add'] = False
    context['save_as'] = False
    context['has_delete_permission'] = False
    context['has_change_permission'] = False
    context['has_add_permission'] = False
    return context


class MemberListView(RestrictedViewList):

    def can_view_all(self):
        """Only staffers should be a"""
        return self.request.user.has_permission("view_all_members")

    def set_restriction_filters(self):
        """Non-staffers should only be able to see themselves"""
        self.restriction_filters["pk__exact"] = self.request.user.pk


class MemberDetailView(UserPassesTestMixin, DetailView):
    """Simple view that displays the all details of a user and provides access to specific change forms"""

    model = Member
    template_name = "admin/core/member/member_detail.html"

    raise_exception = True
    permission_denied_message = "You are not allowed to view another member's personal details!"

    def test_func(self):
        """Only allow members to see the detail page if it is for themselves, or they are staffers"""
        member_to_view = self.get_object()
        is_self = self.request.user.rfid == member_to_view.rfid
        is_staffer = self.request.user.is_staffer
        return is_staffer or is_self

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        return context

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)


class MemberFinishView(UserPassesTestMixin, UpdateView):

    model = Member
    form_class = MemberFinishForm
    template_name_suffix = "_finish"

    raise_exception = True
    permission_denied_message = "You are not allowed complete the sign up process for anyone but yourself!"

    def test_func(self):
        """Only the member themselves is allowed to see the member finish page"""
        member_to_finish = self.get_object()
        return self.request.user.rfid == member_to_finish.rfid

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        return context

    def get_success_url(self):
        return WEB_BASE + reverse("admin:core_member_detail", kwargs={'pk': self.object.pk})
