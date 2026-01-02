from django.utils.translation import gettext_lazy as _

from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    label = "users"
    name = "django_clerk_sdk.users"
    verbose_name = _("Users")

