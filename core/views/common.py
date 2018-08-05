from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView

from ExCSystem.settings import WEB_BASE

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
    field_sets = None

    def get_field_data(self, obj):
        """
        Turn the provided field_sets into a similar structure that makes the field names and values available

        will have the structure:
        [
            (
                "<field_set_name_1",
                [
                    ("<name_1>", value_1, link),
                    ("<name_2>", value_2, link),
                    ...
                    ("<name_n>", value_n, link)
                ]
            ),
            (
                "field_set_name_2",
                [
                    ("<name_1>", value_1, link)
                    ("<name_2>", value_2, link),
                    ...
                    ("<name_n>", value_n, link)
                ]
            ),
        ]

        values will be the string representations of the values saved for the given field
        if the value is a model object, then link will be the url to the related object
        """
        field_data = []
        for set in self.field_sets:
            set_data = []
            set_name = set[0]
            fields = set[1]["fields"]
            data_in_set = []
            for field_name in fields:
                value = getattr(obj, field_name)
                if hasattr(value, "DoesNotExist"):  # This allows us to check if the object is a model
                    app = value._meta.app_label
                    model = value._meta.model_name
                    link = WEB_BASE + reverse(f"admin:{app}_{model}_detail", kwargs={"pk": value.pk})
                else:
                    link = None
                data_in_set.append((field_name, str(value), link))
            set_data.append(set_name)
            set_data.append(data_in_set)
            field_data.append(set_data)

        return field_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        context['field_data'] = self.get_field_data(kwargs['object'])
        return context





