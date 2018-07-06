from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin

from core.models.MemberModels import Member

from ExCSystem.settings.base import WEB_BASE
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


class MemberDetailView(DetailView, UserPassesTestMixin):
    """Simple view that displays the all details of a user and provides access to specific change forms"""

    model = Member
    template_name = "admin/core/member/member_detail.html"

    def test_func(self):
        """Only allow members to see the detail page if it is for themselves, or they are staffers"""
        is_staffer = self.request.user.is_staffer()
        is_self = self.request.user.rfid == self.get_object().rfid
        return is_staffer or is_self

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        return context

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)


class MemberFinishView(UpdateView):

    model = Member
    form_class = MemberFinishForm
    template_name_suffix = "_finish"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        return context

    def get_success_url(self):
        return WEB_BASE + reverse("admin:core_member_detail", kwargs={'pk': self.object.pk})