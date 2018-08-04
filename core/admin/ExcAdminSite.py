from django.contrib.admin import AdminSite


class ExcursionAdmin(AdminSite):
    index_template = "admin_index.html"
    site_header = 'Excursion Admin'
    site_title = 'Excursion Admin'
    index_title = 'Admin Home'


