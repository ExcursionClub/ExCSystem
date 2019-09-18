from django.apps import apps
from django.contrib.admin import AdminSite
from django.urls import NoReverseMatch, reverse
from django.utils.text import capfirst


class ExcursionAdmin(AdminSite):
    index_template = "admin_index.html"

    site_header = "Climbing Club Admin"
    site_title = "Climbing Club Admin"
    index_title = "Admin Home"

    def _build_app_dict(self, request, label=None):
        """
        Ensure that each model with view permissions is viewable in the admin

        By default, the app_dict only includes links to the changelist_view if the user has the 'change' permission for
        the model. Therefore, if the user has a view but not change permission, then there will be no link to the
        changelist . We change this behaviour to include links for models with just view permissions
        """
        app_dict = {}

        # Collect all the models used in either all apps, or just this app
        if label:
            models = {}
            for model, model_admin in self._registry.items():
                if model._meta.app_label == label:
                    models[model] = model_admin
        else:
            models = self._registry

        # Add in each models part of the app_dict
        for model, model_admin in models.items():
            meta_data = model._meta
            app_label = meta_data.app_label
            model_name = meta_data.model_name

            # If the user has no permissions for this model, just omit it entirely
            has_module_perms = model_admin.has_module_permission(request)
            if not has_module_perms:
                continue

            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True not in perms.values():
                continue

            model_dict = {
                "name": capfirst(meta_data.verbose_name_plural),
                "object_name": meta_data.object_name,
                "perms": perms,
            }
            # The changelist is hijacked in the viewable model admin to be the ViewList
            if perms.get("view") or perms.get("change"):
                try:
                    model_dict["admin_url"] = reverse(
                        f"admin:{app_label}_{model_name}_changelist",
                        current_app=self.name,
                    )
                except NoReverseMatch:
                    pass

            if perms.get("add"):
                try:
                    model_dict["add_url"] = reverse(
                        f"admin:{app_label}_{model_name}_add", current_app=self.name
                    )
                except NoReverseMatch:
                    pass

            # Append this model's data to the app dict under the appropriate app_label
            if app_label in app_dict:
                app_dict[app_label]["models"].append(model_dict)

            # If this is the first model in this app, must add the app data in addition to the model data
            else:
                app_dict[app_label] = {
                    "name": apps.get_app_config(app_label).verbose_name,
                    "app_label": app_label,
                    "app_url": reverse(
                        "admin:app_list",
                        kwargs={"app_label": app_label},
                        current_app=self.name,
                    ),
                    "has_module_perms": has_module_perms,
                    "models": [model_dict],
                }

        # If we're only interested in the models for a certain app, only return that subset of the dict
        if label:
            return app_dict.get(label)

        return app_dict
