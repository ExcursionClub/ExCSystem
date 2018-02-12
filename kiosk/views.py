from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic, View

from core.models import GearModels
from kiosk.forms import HomeForm
from core.models.MemberModels import Member


class HomeView(generic.TemplateView):
    template_name = 'home.html'

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['post']
            form = HomeForm()
            # TODO: Add check if gear or member
            return redirect('rfid', text)


class CheckOutView(View):
    template_name = 'kiosk/check_out.html'

    def get(self, request, rfid):
        return render(request, self.template_name, {'rfid': rfid})

    def get_name(self, rfid):
        member_rfids = [member.rfid for member in Member.objects.all()]
        if rfid in member_rfids:
            return rfid.get_full_name()
        else:
            raise ValidationError('This is not associated with a member')
