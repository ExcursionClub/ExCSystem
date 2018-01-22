from django.urls import path

from core.views.GearViews import GearDetailView

urlpatterns = [
    path('gear/<int:pk>/view/', GearDetailView.as_view(), name='gear-detail'),
    # url(r'^$', views.index, name='index'),
]