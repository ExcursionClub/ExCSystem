from api.models import MemberRFIDCheck
from api.views import RFIDCheckLogDetailView, RFIDCheckLogViewList
from core.admin import admin_site
from core.admin.ViewableAdmin import ViewableModelAdmin
from django.contrib.admin import register


class MemberRFIDLogAdmin(ViewableModelAdmin):

    list_display = ('timestamp', 'rfid_checked', 'message', 'was_valid',)
    list_view = RFIDCheckLogViewList
    detail_view_class = RFIDCheckLogDetailView


admin_site.register(MemberRFIDCheck, MemberRFIDLogAdmin)
