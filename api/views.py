from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse

from core.models.MemberModels import Member
from api.models import MemberRFIDCheck

# Create your views here.


class CheckIfActiveMemberView(View):

    def get(self, request, rfid, *args, **kwargs):

        matching_members = list(Member.objects.filter(rfid=rfid))
        num_members = len(matching_members)

        if num_members and matching_members[0].is_active_member:
            valid_member = True
            response = HttpResponse(status=200)
        else:
            valid_member = False
            response = HttpResponse(status=401)

        MemberRFIDCheck.objects.create(rfid_checked=rfid, was_valid=valid_member)
        return response
