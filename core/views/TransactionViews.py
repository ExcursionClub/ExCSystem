from core.views.ViewList import RestrictedViewList


class TransactionListView(RestrictedViewList):

    def can_view_all(self):
        """Non-staffers should only be able to see transactions related to themselves"""
        if self.request.user.is_staffer:
            return True

        else:
            self.restriction_filters["member_id__exact"] = self.request.user.pk
            return False
