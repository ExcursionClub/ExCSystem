"""Master URL config for the project"""

from core.admin import admin_site
from core.views.email import ExcPasswordResetView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = (
    [
        path("", include("frontpage.urls", namespace="front-page")),
        path(
            "admin/password_reset/",
            ExcPasswordResetView.as_view(),
            name="admin_password_reset",
        ),
        path(
            "admin/password_reset/done/",
            auth_views.PasswordResetDoneView.as_view(),
            name="password_reset_done",
        ),
        path(
            "reset/<uidb64>/<token>/",
            auth_views.PasswordResetConfirmView.as_view(),
            name="password_reset_confirm",
        ),
        path(
            "reset/done/",
            auth_views.PasswordResetCompleteView.as_view(),
            name="password_reset_complete",
        ),
        path("admin/", admin_site.urls),
        path("kiosk/", include("kiosk.urls", namespace="kiosk")),
        path("core/", include("core.urls")),
        path("api/", include("api.urls", namespace="api")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
