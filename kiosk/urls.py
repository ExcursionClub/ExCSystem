from django.urls import include, path
from django.contrib.auth.views import LoginView, LogoutView

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='kiosk_login'),
    path('logout/', LogoutView.as_view(), name='kiosk_logout'),
    path('<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
]
