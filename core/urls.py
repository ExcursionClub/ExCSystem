from django.urls import path


from core.views.selectViews import GearImageSelect

urlpatterns = [
    path('AlreadyUploadedImage/select/', GearImageSelect.as_view(), name="gearImageSelect")
]