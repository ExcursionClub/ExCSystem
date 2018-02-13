from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic, View

from core.models import GearModels
from kiosk.forms import HomeForm
from core.models.MemberModels import Member


class HomeView(generic.TemplateView):
    template_name = 'kiosk/home.html'

    def get(self, request):
        form = HomeForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = HomeForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['post']
            form = HomeForm()
            # TODO: Add check if gear or member
            return redirect('check_out', text)


class CheckOutView(View):
    template_name = 'kiosk/check_out.html'

    def get(self, request, rfid):
        name = self.get_name(rfid)
        checked_out_gear = [1,2,3] #self.get_checked_out_gear(rfid)
        args = {'name': name, 'checked_out_gear': checked_out_gear}
        return render(request, self.template_name, args)

    def get_name(self, rfid):
        name = Member.objects.all().filter(rfid=rfid).get().get_full_name()
        if name:
            return name
        else:
            # TODO: Fail soft. Deny redirect from page
            raise ValidationError('This is not associated with a member')
