from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_permission_codename


class ViewableModelAdmin(ModelAdmin):
    """
    A model admin that has an additional view_<model> permission, that allows viewing without editing
    """

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