"""ExCSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from core.admin import admin_site
from core.Email import ExcPasswordResetView

# If you want to change the template to use for the admin set it here
# admin.site.index_template = path/to/the/template.html

urlpatterns = [
    path('kiosk/', include('kiosk.urls')),
    path(
      'admin/password_reset/',
      ExcPasswordResetView.as_view(),
      name='admin_password_reset',
    ),
    path(
      'admin/password_reset/done/',
      auth_views.PasswordResetDoneView.as_view(),
      name='password_reset_done',
    ),
    path(
      'reset/<uidb64>/<token>/',
      auth_views.PasswordResetConfirmView.as_view(),
      name='password_reset_confirm',
    ),
    path(
      'reset/done/',
      auth_views.PasswordResetCompleteView.as_view(),
      name='password_reset_complete',
    ),
    path('admin/', admin_site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
