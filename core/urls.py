from django.urls import path

from core.views.GearViews import GearDetailView

urlpatterns = [
    path('gear/<int:pk>/detail/', GearDetailView.as_view(), name='core_gear_detail'),
]