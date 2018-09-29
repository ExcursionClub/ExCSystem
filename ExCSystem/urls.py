from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from core.admin import admin_site

# If you want to change the template to use for the admin set it here
# admin.site.index_template = path/to/the/template.html

urlpatterns = [
    path('admin/', admin_site.urls),
    path('kiosk/', include('kiosk.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
