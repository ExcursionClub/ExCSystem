from django.urls import path

from core.views.GearViews import GearDetailView
from core.views.MemberViews import MemberDetailView

urlpatterns = [
    path('gear/<int:pk>/detail/', GearDetailView.as_view(), name='core_gear_detail'),
    path('member/<int:pk>/detail/', MemberDetailView.as_view(), name='core_member_detail'),
]