from django.contrib.auth.mixins import UserPassesTestMixin

from core.views.ViewList import RestrictedViewList
from core.views.common import ModelDetailView
from core.models.TransactionModels import Transaction


class TransactionListView(RestrictedViewList):

    def test_func(self):
        return self.request.user.has_permission("view_transaction")

    def can_view_all(self):
        """Non-staffers should only be able to see transactions related to themselves"""
        return self.request.user.has_permission("view_all_transactions")

    def set_restriction_filters(self):
        """If a member cannot see all transactions, they can only see those related to themselves"""
        self.restriction_filters["member_id__exact"] = self.request.user.pk


class TransactionDetailView(UserPassesTestMixin, ModelDetailView):

    model = Transaction

    def test_func(self):
        """Can view the detail of transaction of member is a staffer or transaction involves the member"""
        transaction_to_view = self.get_object()
        try:
            related_to_self = self.request.user.pk == transaction_to_view.member.pk
        except AttributeError:  # Transaction need not have a member
            related_to_self = False
        is_staffer = self.request.user.is_staffer
        return is_staffer or related_to_self

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)
