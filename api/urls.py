from api.views import CheckIfActiveMemberView, ActiveMemberView
from django.urls import include, path

app_name = "api"
urlpatterns = [
    path(
        "memberRFIDcheck/<str:rfid>",
        CheckIfActiveMemberView.as_view(),
        name="memberRFIDcheck",
    ),
    path(
        "active_members",
        ActiveMemberView.as_view(),
        name="all_active_members"
    )
]
