from django.utils import timezone
from django.views.generic import DetailView


def get_default_context(obj, context):
    """Convenience function for getting the default context data of a member"""
    context['now'] = timezone.now()
    context['opts'] = obj.model._meta
    context['app_label'] = obj.model._meta.app_label
    context['change'] = False
    context['is_popup'] = False
    context['add'] = False
    context['save_as'] = False
    context['has_delete_permission'] = False
    context['has_change_permission'] = False
    context['has_add_permission'] = False
    return context


class ModelDetailView(DetailView):

    template_name = "admin/core/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        return context





