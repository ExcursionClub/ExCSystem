from typing import List

from core.models.GearModels import Gear
from core.models.MemberModels import Member
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View, generic
from kiosk.CheckoutLogic import do_checkin, do_checkout
from kiosk.forms import HomeForm, RetagGearForm


class HomeView(LoginRequiredMixin, generic.TemplateView):
    """
    Main kiosk view
    Here gear can be checked in by either scanning an RFID tag or
    typing the RFID number.
    If a member tag is entered the CheckoutView is opened and
    gear can be checked out to that member.
    """
    template_name = 'kiosk/home.html'
    login_url = 'kiosk:login'
    redirect_field_name = ''

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    @staticmethod
    def post(request):
        form = HomeForm(request.POST)
        if form.is_valid():
            rfid = form.cleaned_data['rfid']

            try:
                Gear.objects.get(rfid=rfid)
                return redirect('kiosk:gear', int(rfid))
            except Gear.DoesNotExist:
                pass

            try:
                Member.objects.get(rfid=rfid)
                return redirect('kiosk:check_out', rfid)
            except Member.DoesNotExist:
                pass

            if rfid.isdigit() and len(rfid) == 10:
                alert_message = f'The RFID {rfid} is not registered'
                messages.add_message(request, messages.WARNING, alert_message)
            else:
                alert_message = f'{rfid} is not a valid RFID'
                messages.add_message(request, messages.WARNING, alert_message)

            return redirect('kiosk:home')


class CheckOutView(View):
    """
    Members view of the kiosk
    Contains a list of gear that's rented out by the member
    Check out gear by scanning and RFID tag or typing the RFID number
    """
    template_name = 'kiosk/check_out.html'

    def get(self, request, rfid: str):
        form = HomeForm()
        name = get_name(rfid)
        checked_out_gear = get_checked_out_gear(rfid)
        args = {
            'form': form,
            'name': name,
            'checked_out_gear': checked_out_gear
        }
        return render(request, self.template_name, args)

    @staticmethod
    def post(request, rfid):
        form = HomeForm(request.POST)
        if form.is_valid():
            gear_rfid = form.cleaned_data['rfid']
            staffer_rfid = request.user.rfid
            member_rfid = rfid

            try:
                gear = Gear.objects.get(rfid=gear_rfid)
            except Gear.DoesNotExist:
                gear = None

            if gear:
                if gear.is_available():
                    do_checkout(staffer_rfid, member_rfid, gear.rfid)
                    alert_message = f'{gear.name} was checked out successfully'
                    messages.add_message(request, messages.INFO, alert_message)
                else:
                    alert_message = 'Gear is already rented out'
                    messages.add_message(request, messages.WARNING, alert_message)
            else:
                alert_message = 'The RFID tag is not registered to a piece of gear'
                messages.add_message(request, messages.WARNING, alert_message)

            return redirect('kiosk:check_out', member_rfid)


class RetagGearView(View):
    template_name = 'kiosk/retag_gear.html'

    def get(self, request, rfid: str):
        form = RetagGearForm(initial={'rfid': rfid})
        args = {
            'form': form,
            'rfid': rfid
        }
        return render(request, self.template_name, args)


class GearView(View):
    template_name = 'kiosk/gear.html'

    def get(self, request, rfid: str):
        try:
            gear = Gear.objects.get(rfid=rfid)
        except Gear.DoesNotExist:
            raise Http404()

        return render(request, self.template_name, {'gear': gear})



def get_name(member_rfid: str) -> str:
    try:
        name = Member.objects.get(rfid=member_rfid).get_full_name()
        return name
    except Member.DoesNotExist:
        raise ValidationError('This is not associated with a member')


def get_checked_out_gear(member_rfid: str) -> List[object]:
    try:
        current_member = Member.objects.get(rfid=member_rfid)
        checked_out_gear = list(Gear.objects.filter(checked_out_to=current_member))
        return checked_out_gear
    except Member.DoesNotExist:
        raise ValidationError(f'There is no member with {member_rfid}')
