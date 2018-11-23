from django.views.generic.base import View
from django.http.response import HttpResponse

from core.views.ViewList import RestrictedViewList
from core.views.common import ModelDetailView
from api.models import MemberRFIDCheck

# Create your views here.


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
        return self.request.user.has_permission("view_rfid_check_log")


class RFIDCheckLogDetailView(ModelDetailView):
    model = MemberRFIDCheck

