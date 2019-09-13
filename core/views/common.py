from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.views.generic import DetailView
from uwccsystem.settings import WEB_BASE


def get_default_context(view, context):
    """Convenience function for getting the default context data of a member"""

    is_add = True if view.object else False

    user = view.request.user
    obj_name = view.model._meta.model_name

    context["now"] = timezone.now()
    context["opts"] = view.model._meta
    context["app_label"] = view.model._meta.app_label
    context["is_popup"] = False
    context["add"] = is_add
    context["has_delete_permission"] = user.has_permission(f"core.delete_{obj_name}")
    context["has_change_permission"] = user.has_permission(f"core.change_{obj_name}")
    context["has_add_permission"] = user.has_permission(f"core.add_{obj_name}")
    context["has_view_permission"] = user.has_permission(f"core.view_{obj_name}")

    # Not entirely sure the full meaning of these, but editProfile or detail fail to load if they are not set, Sorry
    context["save_as"] = False
    context["change"] = False

    return context


class ModelDetailView(DetailView):

    template_name = "admin/core/detail.html"
    field_sets = None

    def get_html_repr(self, obj):
        """
        Get the HTML to render the provided fields sets as a table

        will have the structure:

        <table>
            <tr><td>{{set_name}}</td></tr>
            <tr>
                <td>
                    <table>
                        <tr>
                            <td width="10px"></td>
                            <td>{field_name}</td>
                            <td><a href="field url">{field_value}</a></td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr><td>{{set_name}}</td></tr>
            <tr>
                <td>
                    <table>
                        <tr>
                            <td width="10px"></td>
                            <td>{field_name}</td>
                            <td><a href="field url">{field_value}</a></td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>


        values will be the string representations of the values saved for the given field
        if the value is a model object, then link will be the url to the related object
        """

        if self.field_sets:
            field_sets = self.field_sets
        else:
            field_sets = self.get_field_sets(obj)

        lines = []
        lines.append("<table>")
        for set in field_sets:
            set_name = set[0]
            lines.append(f"<tr><td>{set_name}</td></tr>")
            lines.append("<tr>\n<td>\n<table>")
            fields = set[1]["fields"]
            for field_name in fields:
                lines.append("<tr>")
                lines.append('<td width="10px"></td>')
                lines.append(f"<td>{field_name}: </td>")
                value = getattr(obj, field_name)
                simple_line = f"<td>{str(value)}</td>"
                if hasattr(
                    value, "DoesNotExist"
                ):  # This allows us to check if the object is a model
                    app = value._meta.app_label
                    model = value._meta.model_name
                    try:
                        link = WEB_BASE + reverse(
                            f"admin:{app}_{model}_detail", kwargs={"pk": value.pk}
                        )
                    except NoReverseMatch:
                        lines.append(simple_line)
                    else:
                        lines.append(f'<td><a href="{link}">{str(value)}</a></td>')
                else:
                    lines.append(simple_line)
                lines.append("</tr>")
            lines.append("</table>\n</td>\n</tr>")

        lines.append("</table>")

        html = mark_safe("\n".join(lines))
        return html

    @staticmethod
    def get_field_sets(obj):
        field_names = []
        for field in obj._meta.fields:
            field_names.append(field.name)
        return ((f"All {obj._meta.model_name} data", {"fields": field_names}),)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_default_context(self, context)
        context["html_representation"] = self.get_html_repr(kwargs["object"])
        return context
