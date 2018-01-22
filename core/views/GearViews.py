from django.http import HttpResponse
from django.views.generic.detail import DetailView

from django.shortcuts import render
from django.utils import timezone

from core.models.GearModels import Gear


class GearDetailView(DetailView):

    model = Gear

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context