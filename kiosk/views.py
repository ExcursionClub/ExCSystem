from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import generic, View

from core.models import GearModels
from kiosk.forms import HomeForm


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
            return redirect('rfid', text)


class CheckOutView(View):
    template_name = 'kiosk/check_out.html'

    def get(self, request, rfid):
        return render(request, self.template_name, {'rfid': rfid})
