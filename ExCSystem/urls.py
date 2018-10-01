from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from core.admin import admin_site

urlpatterns = [
    path('', include('front_page.urls', namespace='front-page')),
    path('admin/', admin_site.urls),
    path('kiosk/', include('kiosk.urls', namespace='kiosk')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

