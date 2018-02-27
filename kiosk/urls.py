from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
    path('retag/', views.RetagView.as_view(), name='retag'),
]
