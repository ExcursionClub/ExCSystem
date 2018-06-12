from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.utils import timezone

from core.models.MemberModels import Member

from core.forms.MemberForms import (MemberFinishForm, MemberUpdateContactForm, MemberChangeCertsForm,
    MemberChangeRFIDForm, MemberChangeStatusForm, StafferDataForm)


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


class MemberDetailView(DetailView):
    """Simple view that displays the all details of a user and provides access to specific change forms"""

    model = Member
    template_name = "admin/core/member/member_detail.html"

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