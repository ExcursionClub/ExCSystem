from api.views import CheckIfActiveMemberView
from django.urls import include, path

app_name = 'api'
urlpatterns = [
    path('memberRFIDcheck/<str:rfid>', CheckIfActiveMemberView.as_view(), name='memberRFIDcheck'),
]
