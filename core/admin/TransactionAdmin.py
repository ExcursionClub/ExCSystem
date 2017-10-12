from django.contrib import admin


class TransactionAdmin(admin.ModelAdmin):
    list_display = ("type", "timestamp", "gear", "member", "authorizer", "comments")
    list_filter = ("type", )
    search_fields = ("gear__name", "member__first_name", "member__last_name",
                     "authorizer__first_name", "authorizer__last_name")

    def __init__(self, *args, **kwargs):
        super(TransactionAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = []

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Removes the ability to edit the transaction by redirecting all attempts to go to the edit page to view"""
        from django.core.urlresolvers import reverse
        from django.http import HttpResponseRedirect
        # TODO: Currently this redirects back to the list view page. Make it redirect to a detail view page
        return HttpResponseRedirect(reverse('admin:core_transaction_changelist'))

    def has_add_permission(self, request):
        """Nobody should be allowed to manually add transactions"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Nobody should be allowed to manually delete transactions"""
        return False