from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from accounts.models import UserProfile


LOGISTICA_VIEWER = "LogisticaViewer"
LOGISTICA_ADMIN = "LogisticaAdmin"

PERMISSIONS = {
    "access_dashboard": "Can access dashboard",
    "manage_internal_users": "Can manage internal users",
    "view_import_history": "Can view import history",
    "reset_internal_user_password": "Can reset internal user password",
    "export_dashboard": "Can export dashboard",
}

GROUP_PERMISSIONS = {
    LOGISTICA_VIEWER: [
        "access_dashboard",
        "export_dashboard",
    ],
    LOGISTICA_ADMIN: [
        "access_dashboard",
        "export_dashboard",
        "manage_internal_users",
        "view_import_history",
        "reset_internal_user_password",
    ],
}


def setup_rbac():
    permissions = get_or_create_permissions()
    groups = get_or_create_groups()
    assign_group_permissions(groups, permissions)
    created_profiles = ensure_user_profiles()
    return {
        "permissions": permissions,
        "groups": groups,
        "created_profiles": created_profiles,
    }


def get_or_create_permissions():
    content_type = ContentType.objects.get_for_model(UserProfile)
    permissions = {}

    for codename, name in PERMISSIONS.items():
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={"name": name},
        )
        if permission.name != name:
            permission.name = name
            permission.save(update_fields=["name"])
        permissions[codename] = permission

    return permissions


def get_or_create_groups():
    return {
        group_name: Group.objects.get_or_create(name=group_name)[0]
        for group_name in GROUP_PERMISSIONS
    }


def assign_group_permissions(groups, permissions):
    for group_name, codenames in GROUP_PERMISSIONS.items():
        groups[group_name].permissions.set([permissions[codename] for codename in codenames])


def ensure_user_profiles():
    User = get_user_model()
    created_count = 0

    for user in User.objects.all():
        _, created = UserProfile.objects.get_or_create(user=user)
        if created:
            created_count += 1

    return created_count
