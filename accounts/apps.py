from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_roles(sender, **kwargs):
    from django.contrib.auth.models import Group
    from .permissions import ROLES
    for role in ROLES:
        Group.objects.get_or_create(name=role)


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        post_migrate.connect(create_roles, sender=self)
