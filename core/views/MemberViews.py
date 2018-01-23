from django.views.generic.detail import DetailView
from django.utils import timezone

from core.models.MemberModels import Member


class MemberDetailView(DetailView):

    model = Member

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['opts'] = self.model._meta
        context['app_label'] = self.model._meta.app_label
        context['change'] = False
        context['is_popup'] = False
        context['add'] = False
        context['save_as'] = False
        context['has_delete_permission'] = False
        context['has_change_permission'] = False
        context['has_add_permission'] = False
        return context
