from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db import transaction

from accounts.models import UserProfile
from accounts.services.rbac_service import GROUP_PERMISSIONS


User = get_user_model()


def get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile


def list_internal_users():
    ensure_internal_profiles()
    return User.objects.select_related("profile").prefetch_related("groups").order_by(
        "username"
    )


@transaction.atomic
def create_internal_user(cleaned_data):
    user = User.objects.create_user(
        username=cleaned_data["username"],
        password=cleaned_data["password1"],
        first_name=cleaned_data.get("first_name", ""),
        last_name=cleaned_data.get("last_name", ""),
        email=cleaned_data.get("email", ""),
        is_active=cleaned_data.get("is_active", True),
    )
    set_authorized_groups(user, cleaned_data.get("groups", []))

    profile = get_user_profile(user)
    profile.must_change_password = True
    profile.save(update_fields=["must_change_password", "updated_at"])

    return user


@transaction.atomic
def update_internal_user(user, cleaned_data, actor):
    ensure_can_manage_target(user, actor)

    user.first_name = cleaned_data.get("first_name", "")
    user.last_name = cleaned_data.get("last_name", "")
    user.email = cleaned_data.get("email", "")
    user.is_active = cleaned_data.get("is_active", False)
    user.save(update_fields=["first_name", "last_name", "email", "is_active"])
    set_authorized_groups(user, cleaned_data.get("groups", []))

    return user


@transaction.atomic
def toggle_user_active(user, actor):
    ensure_can_manage_target(user, actor)

    if user == actor and user.is_active:
        raise PermissionDenied("Você não pode desativar o próprio usuário.")

    user.is_active = not user.is_active
    user.save(update_fields=["is_active"])
    return user


@transaction.atomic
def reset_internal_user_password(user, temporary_password, actor):
    ensure_can_manage_target(user, actor)

    user.set_password(temporary_password)
    user.save(update_fields=["password"])

    profile = get_user_profile(user)
    profile.must_change_password = True
    profile.save(update_fields=["must_change_password", "updated_at"])

    return user


@transaction.atomic
def mark_password_changed(user):
    profile = get_user_profile(user)
    profile.must_change_password = False
    profile.save(update_fields=["must_change_password", "updated_at"])
    return profile


def set_authorized_groups(user, groups):
    allowed_names = set(GROUP_PERMISSIONS.keys())
    current_unauthorized_groups = user.groups.exclude(name__in=allowed_names)
    user.groups.set([*current_unauthorized_groups, *groups])


def ensure_internal_profiles():
    for user in User.objects.filter(profile__isnull=True):
        UserProfile.objects.get_or_create(user=user)


def ensure_can_manage_target(user, actor):
    if user.is_superuser and not actor.is_superuser:
        raise PermissionDenied("Usuários técnicos não podem ser alterados por usuário operacional.")
