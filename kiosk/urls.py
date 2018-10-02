from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

from . import views


app_name = 'kiosk'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('member/<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
    path('retag-gear/<int:rfid>/', views.RetagGearView.as_view(), name='retag_gear')
]
