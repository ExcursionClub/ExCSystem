from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse


class ViewList(ChangeList):
    """
    List display class that instead of linking to the change page, links to the detail view page
    """

    def __init__(self, *args, **kwargs):
        super(ViewList, self).__init__(*args, **kwargs)
        self.title = f'Select the {self.opts.verbose_name} to view'

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('admin:{}_{}_detail'.format(self.opts.app_label, self.opts.model_name),
                       args=(quote(pk),),
                       current_app=self.model_admin.admin_site.name)


class RestrictedViewList(UserPassesTestMixin, ViewList):
    """
    List display that will not display for unauthorized users and/or only shows certain objects to certain users
    """

    raise_exception = True
    permission_denied_message = "You are not allowed to view this list!"

    # Dict describing the filters to be applied when restricting the list. For example {'groups__id__exact' : 1} would
    # only display those items that are members of group one. Look at querysets filter for more information
    restriction_filters = {}

    def __init__(self, request, *args, **kwargs):
        """Pass instantiation to the parent after saving the request data"""
        self.request = request
        super(RestrictedViewList, self).__init__(request, *args, **kwargs)

    def test_func(self):
        """Override this to determine if the user is allowed to see this list"""
        return True

    def can_view_all(self):
        """
        Override this to determine when a user is allowed to view all list elements
        """
        return self.request.user.is_staffer

    def set_restriction_filters(self):
        """
        If a member is not allowed to view the whole list, the filters set here will be applied to the listed items
        """
        pass

    def get_queryset(self, request):

        queryset = super(RestrictedViewList, self).get_queryset(request)

        # If the user is not allowed to view all the items, additionally filter the gotten queryset before returning it
        if not self.can_view_all():
            self.set_restriction_filters()
            queryset = queryset.filter(**self.restriction_filters)

        return queryset

