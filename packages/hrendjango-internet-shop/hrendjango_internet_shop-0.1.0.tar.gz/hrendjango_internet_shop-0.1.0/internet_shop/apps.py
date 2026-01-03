from django.apps import AppConfig
from django.utils.translation import gettext_lazy


class InternetShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internet_shop'
    verbose_name = gettext_lazy('Internet Shop')