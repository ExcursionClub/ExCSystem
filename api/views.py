from api.models import MemberRFIDCheck
from core.models.MemberModels import Member
from core.views.common import ModelDetailView
from core.views.ViewList import RestrictedViewList
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from django.views.generic.base import View

# Create your views here.


class ActiveMemberView(LoginRequiredMixin, UserPassesTestMixin,TemplateView):

    template_name = "admin/api/active_members.html"

    def test_func(self):
        return self.request.user.has_permission('core.view_all_members')

    def get_context_data(self, **kwargs):
        context = super(ActiveMemberView, self).get_context_data(**kwargs)

        members = Member.objects.all().exclude(group='Expired')
        emails = [f"{member.email}\n" for member in members if member.is_active_member]

        context['emails'] = emails
        return context


class CheckIfActiveMemberView(View):
    def get(self, request, rfid, *args, **kwargs):

        valid_member = MemberRFIDCheck.objects.create(rfid=rfid)

        if valid_member:
            response = HttpResponse(status=200)
        else:
            response = HttpResponse(status=401)

        return response


class RFIDCheckLogViewList(RestrictedViewList):
    def test_func(self):
        return self.request.user.has_permission("core.view_rfid_check_log")


class RFIDCheckLogDetailView(ModelDetailView):
    model = MemberRFIDCheck
