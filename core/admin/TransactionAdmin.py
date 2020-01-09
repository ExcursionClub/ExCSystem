from core.admin.ViewableAdmin import ViewableModelAdmin
from core.views.TransactionViews import TransactionDetailView, TransactionListView


class TransactionAdmin(ViewableModelAdmin):
    list_display = ("type", "timestamp", "gear", "member", "authorizer", "comments")
    list_filter = ("type",)
    search_fields = (
        "gear__geartype__name",
        "gear__gear_data",
        "member__first_name",
        "member__last_name",
        "authorizer__first_name",
        "authorizer__last_name",
    )
    list_view = TransactionListView
    detail_view_class = TransactionDetailView

    def __init__(self, *args, **kwargs):
        super(TransactionAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = []

    def has_add_permission(self, request):
        """Nobody should be allowed to manually add transactions"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Nobody should be allowed to manually delete transactions"""
        return False
