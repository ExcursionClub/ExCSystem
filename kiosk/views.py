from django.views import generic

from core.models import GearModels


class CheckOutView(generic.ListView):
    template_name = 'kiosk/check_out.html'

    def get_queryset(self):
        # Not sure what this does
        return GearModels.Gear.objects
