from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
    path('retag/department', views.RetagDepartmentView.as_view(), name='retag_department'),
    path('retag/gear_type', views.RetagGearView.as_view(), name='retag_gear_type'),
]
