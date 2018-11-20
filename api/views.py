from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse

from core.models.MemberModels import Member

# Create your views here.


class CheckIfActiveMemberView(View):

    def get(self, request, rfid, *args, **kwargs):

        matching_members = list(Member.objects.filter(rfid=rfid))
        num_members = len(matching_members)

        if num_members and matching_members[0].is_active_member:
            response = HttpResponse(status=200)
        else:
            response = HttpResponse(status=401)

        return response
