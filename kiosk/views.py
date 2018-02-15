from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic, View

from core.models.GearModels import Gear
from core.models.MemberModels import Member
from kiosk.CheckoutLogic import do_checkout
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
        form = HomeForm()
        name = self.get_name(rfid)
        checked_out_gear = self.get_checked_out_gear(rfid)
        args = {'form': form, 'name': name, 'checked_out_gear': checked_out_gear}
        return render(request, self.template_name, args)

    def post(self, request, rfid):
        form = HomeForm(request.POST)
        if form.is_valid():
            gear_rfid = form.cleaned_data['rfid']
            # TODO: Check that RFID isn't already used
            staffer_rfid = '1234567890'
            member_rfid = '1234567890'
            # Get random gear RFID
            # TODO: Add gear with known gear id for testing
            gear = Gear.objects.filter(rfid=gear_rfid).get()
            if gear.is_available():
                do_checkout(staffer_rfid, member_rfid, gear.rfid)
            return redirect('check_out', member_rfid)

    def get_name(self, member_rfid):
        name = Member.objects.filter(rfid=member_rfid).get().get_full_name()
        if name:
            return name
        else:
            # TODO: Fail soft. Deny redirect from page
            raise ValidationError('This is not associated with a member')

    def get_checked_out_gear(self, member_rfid):
        current_member = Member.objects.filter(rfid=member_rfid).first()
        checked_out_gear = list(Gear.objects.filter(checked_out_to=current_member))
        return checked_out_gear
