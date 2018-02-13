from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic, View

from core.models.GearModels import Gear
from core.models.MemberModels import Member
from kiosk.forms import HomeForm


class HomeView(generic.TemplateView):
    template_name = 'kiosk/home.html'

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['rfid']
            # TODO: Add check if gear or member
            return redirect('check_out', text)


class CheckOutView(View):
    template_name = 'kiosk/check_out.html'

    def get(self, request, rfid):
        name = self.get_name(rfid)
        checked_out_gear = self.get_checked_out_gear(rfid)
        args = {'name': name, 'checked_out_gear': checked_out_gear}
        return render(request, self.template_name, args)

    def get_name(self, rfid):
        name = Member.objects.filter(rfid=rfid).get().get_full_name()
        if name:
            return name
        else:
            # TODO: Fail soft. Deny redirect from page
            raise ValidationError('This is not associated with a member')

    def get_checked_out_gear(self, rfid):
        current_member = Member.objects.filter(rfid=rfid).first()
        checked_out_gear = list(Gear.objects.filter(checked_out_to=current_member))
        return checked_out_gear
