from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(template_name='kiosk/login.html')),
    path('logged_in/', views.logged_in, name='logged_in'),
]
