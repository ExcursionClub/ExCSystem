from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import DetailView

from core.views.ViewList import RestrictedViewList
from core.models.TransactionModels import Transaction


class TransactionListView(RestrictedViewList):

    def can_view_all(self):
        """Non-staffers should only be able to see transactions related to themselves"""
        if self.request.user.is_staffer:
            return True

        else:
            self.restriction_filters["member_id__exact"] = self.request.user.pk
            return False


class TransactionDetailView(UserPassesTestMixin, DetailView):

    model = Transaction
    template_name = "admin/core/member/transaction_detail.html"

    def test_func(self):
        """Can view the detail of transaction of member is a staffer or transaction involves the member"""
        transaction_to_view = self.get_object()
        related_to_self = self.request.user.pk == transaction_to_view.member.pk
        is_staffer = self.request.user.is_staffer
        return is_staffer or related_to_self

    def post(self, request, *args, **kwargs):
        """Treat post requests as get requests"""
        return self.get(request, *args, **kwargs)
