from django.views.generic.list import ListView
from core.models.FileModels import AlreadyUploadedImage


class GearImageSelect(ListView):

    model = AlreadyUploadedImage


