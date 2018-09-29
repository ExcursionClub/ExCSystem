from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from core.admin import admin_site

urlpatterns = [
    path('', include('front_page.urls')),
    path('admin/', admin_site.urls),
    path('kiosk/', include('kiosk.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
