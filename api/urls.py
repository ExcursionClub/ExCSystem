from django.urls import include, path
from api.views import CheckIfActiveMemberView


app_name = 'kiosk'
urlpatterns = [
    path('memberRFIDcheck/<str:rfid>', CheckIfActiveMemberView.as_view(), name='memberRFIDcheck'),
]