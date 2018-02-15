from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote
from django.urls import reverse


class ViewList(ChangeList):
    """
    List display class that instead of linking to the change page, links to the detail view page
    """

    def url_for_result(self, result):
        pk = getattr(result, self.pk_attname)
        return reverse('admin:{}_{}_detail'.format(self.opts.app_label, self.opts.model_name),
                       args=(quote(pk),),
                       current_app=self.model_admin.admin_site.name)