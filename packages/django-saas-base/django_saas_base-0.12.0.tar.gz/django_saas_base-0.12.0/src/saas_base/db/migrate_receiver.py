import typing as t
from django.apps import apps as global_apps
from django.db import DEFAULT_DB_ALIAS

if t.TYPE_CHECKING:
    from ..models import Permission, Role


def create_permissions_receiver(permissions: t.List[t.Tuple[str, str]]):
    def _create_permissions(app_config, verbosity=2, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
        if not app_config.models_module:
            return

        if app_config.label != 'saas_base':
            return

        try:
            permission_cls: t.Type['Permission'] = apps.get_model(app_config.label, 'Permission')
        except LookupError:
            return

        existed_perms = set(permission_cls.objects.values_list('name', flat=True).all())

        to_add_perms = []
        for name, description in permissions:
            if name not in existed_perms:
                to_add_perms.append(permission_cls(name=name, description=description))

        if to_add_perms:
            permission_cls.objects.using(using).bulk_create(to_add_perms, ignore_conflicts=True)
        if verbosity >= 2:
            for perm in to_add_perms:
                print(f"Adding saas_base.Permission '{perm.name}'")

    return _create_permissions


def create_roles_receiver(roles: t.List[t.Tuple[str, str, t.List[str]]]):
    def _create_roles(app_config, verbosity=2, using=DEFAULT_DB_ALIAS, apps=global_apps, **kwargs):
        if not app_config.models_module:
            return

        if app_config.label != 'saas_base':
            return

        try:
            role_cls: t.Type['Role'] = apps.get_model(app_config.label, 'Role')
        except LookupError:
            return

        for name, description, perms in roles:
            role, created = role_cls.objects.using(using).update_or_create(
                name=name,
                defaults={'description': description},
            )
            role.permissions.set(perms)

            if created and verbosity >= 2:
                print(f"Adding saas_base.Role '{role.name}'")

    return _create_roles
