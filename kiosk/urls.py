from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from . import views

app_name = "kiosk"
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("", include("django.contrib.auth.urls")),
    path("gear/<slug:rfid>/", views.GearView.as_view(), name="gear"),
    path("member/<slug:rfid>/", views.CheckOutView.as_view(), name="check_out"),
    path("retag-gear/<slug:rfid>/", views.RetagGearView.as_view(), name="retag_gear"),
]
