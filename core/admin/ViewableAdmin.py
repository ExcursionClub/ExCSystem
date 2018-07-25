from functools import update_wrapper
from django.urls import path
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_permission_codename
from django.views.generic.detail import DetailView

from core.views.ViewList import ViewList


class ViewableModelAdmin(ModelAdmin):
    """
    A model admin that has an additional view_<model> permission, that allows viewing without editing
    """

    list_view = ViewList
    detail_view_class = DetailView

    @property
    def detail_view(self):
        return self.detail_view_class.as_view()

    def has_view_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('view', opts)
        return request.user.has_perm("%s.%s" % (opts.app_label, codename))

    def get_model_perms(self, request):
        """
        Return a dict of all perms for this model. This dict has the keys
        ``add``, ``change``, and ``delete`` mapping to the True/False for each
        of those actions.
        """
        return {
            'add': self.has_add_permission(request),
            'change': self.has_change_permission(request),
            'delete': self.has_delete_permission(request),
            'view': self.has_view_permission(request)
        }

    def get_changelist(self, request, **kwargs):
        return self.list_view

    def get_urls(self):
        """Override that adds the url for the detail page of the model"""

        urlpatterns = super().get_urls()

        # Wrapper allows automatic checking of permissions
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        app_label = self.model._meta.app_label
        model_name = self.model._meta.model_name

        # Register the url that will show the detail page for this model
        view_urls = [
            path('<int:pk>/detail/', wrap(self.detail_view), name=f'{app_label}_{model_name}_detail'),
        ]
        return urlpatterns + view_urls
