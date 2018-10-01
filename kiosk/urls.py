from django.urls import include, path

from . import views


app_name = 'kiosk'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('', include('django.contrib.auth.urls')),
    path('member/<int:rfid>/', views.CheckOutView.as_view(), name='check_out'),
    path('tag-gear/<int:rfid>/', views.TagGearView.as_view(), name='tag_gear')
]
