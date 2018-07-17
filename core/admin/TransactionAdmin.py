from django.contrib import admin

from core.views.TransactionViews import TransactionListView


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("type", "timestamp", "gear", "member", "authorizer", "comments")
    list_filter = ("type", )
    search_fields = ("gear__name", "member__first_name", "member__last_name",
                     "authorizer__first_name", "authorizer__last_name")

    def __init__(self, *args, **kwargs):
        super(TransactionAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = []

    def get_changelist(self, request, **kwargs):
        return TransactionViewList

    def has_add_permission(self, request):
        """Nobody should be allowed to manually add transactions"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Nobody should be allowed to manually delete transactions"""
        return False