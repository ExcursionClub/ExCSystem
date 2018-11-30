from django.urls import path

from . import views

app_name = 'front_page'
urlpatterns = [
    path('', views.index, name='home')
]
