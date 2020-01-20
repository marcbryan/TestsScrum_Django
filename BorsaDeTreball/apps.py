
from django.contrib.admin.apps import AdminConfig


class MyAdminConfig(AdminConfig):
    default_site = 'BorsaDeTreball.admin.MyAdminSite'
    site_title = "hollllaaaaa"
    site_header = "hollllaaaaa2"
