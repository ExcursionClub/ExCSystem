from typing import List

from core.models.GearModels import Gear
from core.models.MemberModels import Member
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse
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

    template_name = "kiosk/home.html"
    login_url = "kiosk:login"
    redirect_field_name = ""

    def get(self, request, *args, **kwargs):
        """Render the basic view"""
        form = HomeForm()
        return render(request, self.template_name, {"form": form})

    @staticmethod
    def post(request):
        """On form submission, determine which kiosk view we should go to depending on the submitted RFID"""
        form = HomeForm(request.POST)

        if form.is_valid():
            rfid = form.cleaned_data["rfid"]

            # If the scaned RFID belongs to gear, go to the relevant gear view
            try:
                Gear.objects.get(rfid=rfid)
                return redirect("kiosk:gear", rfid)
            except Gear.DoesNotExist:
                pass

            # If the scaned RFID belongs to a member, go to the relevant member view
            try:
                Member.objects.get(rfid=rfid)
                return redirect("kiosk:check_out", rfid)
            except Member.DoesNotExist:
                pass

            # Something probably went wrong, so try and figure out what it might be
            if rfid.isdigit() and len(rfid) == 10:
                alert_message = f"The RFID {rfid} is not registered"
                messages.add_message(request, messages.WARNING, alert_message)
            else:
                alert_message = f"{rfid} is not a valid RFID"
                messages.add_message(request, messages.WARNING, alert_message)

            return redirect("kiosk:home")


class CheckOutView(View):
    """
    Members view of the kiosk
    Contains a list of gear that's rented out by the member
    Check out gear by scanning and RFID tag or typing the RFID number
    """

    template_name = "kiosk/check_out.html"

    def get(self, request, rfid: str):
        """Render the member view, collect relevant data, and warn if the member is not yet active"""
        form = HomeForm()

        try:
            member = get_member(rfid)
        except ValidationError:
            messages.add_message(request, messages.WARNING, "There is no member with this RFID!")
            return redirect("kiosk:home")

        # Display a warning if the member is not fully active
        if not member.is_active_member:
            alert_message = "Members must be active (have filled out new member email) to rent gear!"
            messages.add_message(request, messages.WARNING, alert_message)

        checked_out_gear = get_checked_out_gear(rfid)

        args = {
            "form": form,
            "member": member,
            "checked_out_gear": checked_out_gear,
            "kiosk_home": reverse("kiosk:home")}
        return render(request, self.template_name, args)

    @staticmethod
    def post(request, rfid):
        form = HomeForm(request.POST)
        if form.is_valid():
            gear_rfid = form.cleaned_data["rfid"]
            staffer_rfid = request.user.rfid
            member_rfid = rfid

            try:
                gear = Gear.objects.get(rfid=gear_rfid)
            except Gear.DoesNotExist:
                gear = None

            if gear:
                # Check the scanned piece of gear in or out, depending on the current state
                if gear.is_available():
                    do_checkout(staffer_rfid, member_rfid, gear_rfid)
                    alert_message = f"{gear.name} was checked out successfully"
                    messages.add_message(request, messages.INFO, alert_message)
                else:
                    do_checkin(staffer_rfid, gear_rfid)
                    alert_message = f"{gear.name} was checked in successfully"
                    messages.add_message(request, messages.WARNING, alert_message)
            else:
                alert_message = "The RFID tag is not registered to a piece of gear"
                messages.add_message(request, messages.WARNING, alert_message)

            return redirect("kiosk:check_out", member_rfid)


class GearView(View):
    template_name = "kiosk/gear.html"

    def get(self, request, rfid: str):
        try:
            gear = Gear.objects.get(rfid=rfid)
        except Gear.DoesNotExist:
            raise Http404()

        args = {"form": HomeForm(), "gear": gear, "kiosk_home": reverse("kiosk:home")}
        return render(request, self.template_name, args)

    @staticmethod
    def post(request, rfid: str):
        """
        Check in item or check it out to a member

        :param rfid: the RFID of the piece of gear displayed on the page
        """

        form = HomeForm(request.POST)
        if form.is_valid():
            form_rfid = form.cleaned_data["rfid"]
            staffer_rfid = request.user.rfid

            try:
                this_gear = Gear.objects.get(rfid=rfid)
            except Gear.DoesNotExist:
                raise Http404()

            # See if the newly scanned RFID belongs to a piece of gear
            try:
                gear = Gear.objects.get(rfid=form_rfid)
                gear_rfid = form_rfid
            except Gear.DoesNotExist:
                gear = None
                gear_rfid = None

            # See if the available RFID belong to members
            try:
                member = Member.objects.get(rfid=form_rfid)
                member_rfid = form_rfid
            except Member.DoesNotExist:
                member = None
                member_rfid = None

            # If we scanned a member RFID, then try to check this piece of gear out to a member
            if member:

                # If this gear is already rented out, just redirect to the member view
                if this_gear.is_rented_out():
                    return redirect("kiosk:check_out", member_rfid)

                # If this gear is not yet checked out, then try to check it our the just scanned member
                else:
                    try:
                        do_checkout(staffer_rfid, member_rfid, rfid)
                    except ValidationError as e:
                        messages.add_message(request, messages.ERROR, e.message)
                    else:
                        alert_message = f"Gear checked out to: {member}!"
                        messages.add_message(request, messages.WARNING, alert_message)
                    finally:
                        return redirect("kiosk:gear", rfid)

            elif gear:

                # If the same piece of gear was scanned, then to to check the gear back in
                if gear_rfid == rfid:
                    if gear.is_rented_out():
                        try:
                            do_checkin(staffer_rfid, gear.rfid)
                        except ValidationError as e:
                            messages.add_message(request, messages.ERROR, e.message)
                        else:
                            alert_message = f"{gear.name} was checked in successfully"
                            messages.add_message(request, messages.INFO, alert_message)
                    else:
                        alert_message = "Gear is already checked in"
                        messages.add_message(request, messages.WARNING, alert_message)

                # If gear was scanned, always redirect to the view for that piece of gear. If this was not the same
                # piece of gear as the current, then it will simply move to the new piece of gear
                return redirect("kiosk:gear", gear_rfid)

            # If no valid rfid was scanned, return to the same page with a warning
            else:
                alert_message = "The RFID is not registered to any gear"
                messages.add_message(request, messages.WARNING, alert_message)

                return redirect("kiosk:gear", rfid)


class RetagGearView(View):
    template_name = "kiosk/retag_gear.html"

    def get(self, request, rfid: str):
        form = RetagGearForm(initial={"rfid": rfid})
        args = {"form": form, "rfid": rfid}
        return render(request, self.template_name, args)


def get_member(member_rfid: str, member=None) -> Member:
    try:
        member = Member.objects.get(rfid=member_rfid)
    except Member.DoesNotExist:
        raise ValidationError("This RFID is not assiciated with a member!")
    else:
        return member


def get_checked_out_gear(member_rfid: str) -> List[object]:

    current_member = get_member(member_rfid)

    try:
        checked_out_gear = list(Gear.objects.filter(checked_out_to=current_member).order_by('due_date'))
    except Member.DoesNotExist:
        raise ValidationError(f"Failed to get a gear list for {current_member.get_full_name()}")
    else:
        return checked_out_gear
