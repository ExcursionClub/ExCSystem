from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
]
