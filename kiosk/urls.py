from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('check_out/', views.check_out, name='check_out'),
]
