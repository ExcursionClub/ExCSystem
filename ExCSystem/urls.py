from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from core.admin import admin_site
from core.Email import ExcPasswordResetView

urlpatterns = [
    path('', include('front_page.urls')),
    path('admin/', admin_site.urls),
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
    path('kiosk/', include('kiosk.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
