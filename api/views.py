from django.shortcuts import render
from django.views.generic.base import View
from django.http.response import HttpResponse

from core.models.MemberModels import Member
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
