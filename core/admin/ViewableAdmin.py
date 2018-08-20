from functools import update_wrapper

from django.contrib.admin.options import csrf_protect_m, IncorrectLookupParameters
from django.contrib.admin.views.main import ERROR_FLAG
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse, SimpleTemplateResponse
from django.urls import path
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_permission_codename
from django.utils.translation import gettext as _, ngettext

from core.views.ViewList import RestrictedViewList
from core.views.common import ModelDetailView


class ViewableModelAdmin(ModelAdmin):
    """
    A model admin that has an additional view_<model> permission, that allows viewing without editing
    """

    list_view = RestrictedViewList
    detail_view_class = ModelDetailView

    def get_detail_view(self):
        """Get the detail view as a view (function) wrapped to automatically check permissions"""

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        detail = self.detail_view_class
        detail.field_sets = self.fieldsets
        detail_view = detail.as_view()
        return wrap(detail_view)

    def has_view_permission(self, request):
        opts = self.opts
        codename = get_permission_codename('view', opts)
        return request.user.has_perm(f'{opts.app_label}.{codename}')

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

    @csrf_protect_m
    def viewlist_view(self, request):
        """
        Same as the change list, but no actions and does not accept post

        Note most of this method is a simplification of the overridden method. Blame django for any wackiness
        """

        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_view_permission(request):
            raise PermissionDenied

        try:
            cl = self.get_changelist_instance(request)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET:
                return SimpleTemplateResponse('admin/invalid_setup.html', {
                    'title': _('Database error'),
                })
            return HttpResponseRedirect(f'{request.path}?ERROR_FLAG=1')

        # This is used in the backend, do not remove
        FormSet = self.get_changelist_formset(request)
        formset = cl.formset = FormSet(queryset=cl.result_list)

        selection_note_all = ngettext(
            '%(total_count)s selected',
            'All %(total_count)s selected',
            cl.result_count
        )

        context = dict(
            self.admin_site.each_context(request),
            module_name=str(opts.verbose_name_plural),
            selection_note=_(f'0 of {len(cl.result_list)} selected'),
            selection_note_all=selection_note_all % {'total_count': cl.result_count},
            title=cl.title,
            is_popup=cl.is_popup,
            to_field=cl.to_field,
            cl=cl,
            has_add_permission=self.has_add_permission(request),
            opts=cl.opts,
            actions_on_top=self.actions_on_top,
            actions_on_bottom=self.actions_on_bottom,
            actions_selection_counter=self.actions_selection_counter,
            preserved_filters=self.get_preserved_filters(request),
        )

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.change_list_template or [
            f'admin/{app_label}/{opts.model_name}/change_list.html',
            f'admin/{app_label}/change_list.html',
            'admin/change_list.html'
        ], context)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        The 'change list' admin view for this model.
        """
        if self.has_change_permission(request):
            return super(ViewableModelAdmin, self).changelist_view(request, extra_context=extra_context)
        else:
            return self.viewlist_view(request)

    def get_urls(self):
        """Override that adds the url for the detail page of the model"""

        app = self.model._meta.app_label
        model = self.model._meta.model_name

        # Register the url that will show the detail page for this model
        view_url = [
            path('<int:pk>/detail/', self.get_detail_view(), name=f'{app}_{model}_detail'),
        ]

        # view_url has to be at the front of the list, because url patterns contains a <pk>/ url pattern which will
        # match any member url containing an id
        urlpatterns = super(ViewableModelAdmin, self).get_urls()
        return view_url + urlpatterns
