from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from accounts.models import UserProfile
from accounts.services.rbac_service import (
    LOGISTICA_ADMIN,
    LOGISTICA_VIEWER,
    setup_rbac,
)
from accounts.services.user_service import (
    create_internal_user,
    reset_internal_user_password,
)


User = get_user_model()


class UserProfileTests(TestCase):
    def test_user_profile_is_created_automatically_for_new_user(self):
        user = User.objects.create_user(username="new-user", password="SafePass!2026")

        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        self.assertFalse(user.profile.must_change_password)


class RbacSetupTests(TestCase):
    def test_setup_rbac_creates_expected_groups(self):
        setup_rbac()

        self.assertTrue(Group.objects.filter(name=LOGISTICA_VIEWER).exists())
        self.assertTrue(Group.objects.filter(name=LOGISTICA_ADMIN).exists())

    def test_setup_rbac_is_idempotent(self):
        setup_rbac()
        first_group_count = Group.objects.count()
        first_permission_count = self._logistics_permission_count()

        setup_rbac()

        self.assertEqual(Group.objects.count(), first_group_count)
        self.assertEqual(self._logistics_permission_count(), first_permission_count)

    def test_logistica_viewer_receives_expected_permissions(self):
        setup_rbac()
        group = Group.objects.get(name=LOGISTICA_VIEWER)

        self.assertEqual(
            set(group.permissions.values_list("codename", flat=True)),
            {"access_dashboard", "export_dashboard"},
        )

    def test_logistica_admin_receives_expected_permissions(self):
        setup_rbac()
        group = Group.objects.get(name=LOGISTICA_ADMIN)

        self.assertEqual(
            set(group.permissions.values_list("codename", flat=True)),
            {
                "access_dashboard",
                "export_dashboard",
                "manage_internal_users",
                "view_import_history",
                "reset_internal_user_password",
            },
        )

    def test_setup_rbac_creates_profiles_for_existing_users(self):
        user = User.objects.create_user(username="legacy-user", password="SafePass!2026")
        user.profile.delete()

        result = setup_rbac()

        self.assertEqual(result["created_profiles"], 1)
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def _logistics_permission_count(self):
        content_type = ContentType.objects.get_for_model(UserProfile)
        codenames = [permission[0] for permission in UserProfile._meta.permissions]
        return Permission.objects.filter(
            content_type=content_type,
            codename__in=codenames,
        ).count()


class InternalUserServiceTests(TestCase):
    def setUp(self):
        setup_rbac()
        self.admin = User.objects.create_user(username="admin", password="SafePass!2026")

    def test_created_user_must_change_password(self):
        group = Group.objects.get(name=LOGISTICA_VIEWER)

        user = create_internal_user(
            {
                "username": "viewer",
                "password1": "TmpAccess!2026",
                "first_name": "Viewer",
                "last_name": "",
                "email": "viewer@example.com",
                "is_active": True,
                "groups": [group],
            }
        )

        user.profile.refresh_from_db()
        self.assertTrue(user.profile.must_change_password)
        self.assertTrue(user.groups.filter(name=LOGISTICA_VIEWER).exists())

    def test_internal_password_reset_marks_password_change_required(self):
        user = User.objects.create_user(username="viewer", password="OldAccess!2026")
        user.profile.must_change_password = False
        user.profile.save(update_fields=["must_change_password"])

        reset_internal_user_password(user, "TmpAccess!2026", self.admin)

        user.refresh_from_db()
        self.assertTrue(user.check_password("TmpAccess!2026"))
        self.assertTrue(user.profile.must_change_password)


class ForcePasswordChangeViewTests(TestCase):
    def test_force_password_change_updates_password_and_clears_flag(self):
        user = User.objects.create_user(username="viewer", password="TmpAccess!2026")
        user.profile.must_change_password = True
        user.profile.save(update_fields=["must_change_password"])
        self.client.force_login(user)

        response = self.client.post(
            reverse("accounts:force_password_change"),
            {
                "new_password1": "NewAccess!2026",
                "new_password2": "NewAccess!2026",
            },
        )

        user.refresh_from_db()
        self.assertRedirects(response, reverse("core:home"))
        self.assertTrue(user.check_password("NewAccess!2026"))
        self.assertFalse(user.profile.must_change_password)


class InternalUserViewPermissionTests(TestCase):
    def setUp(self):
        setup_rbac()
        self.user = User.objects.create_user(username="plain", password="SafePass!2026")
        self.viewer = User.objects.create_user(username="viewer", password="SafePass!2026")
        self.admin = User.objects.create_user(username="admin", password="SafePass!2026")

        self.viewer.groups.add(Group.objects.get(name=LOGISTICA_VIEWER))
        self.admin.groups.add(Group.objects.get(name=LOGISTICA_ADMIN))

    def test_user_without_permission_cannot_access_user_list(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("accounts:user_list"))

        self.assertEqual(response.status_code, 403)

    def test_logistica_admin_can_access_user_list(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("accounts:user_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/user_list.html")

    def test_logistica_viewer_cannot_access_user_list(self):
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("accounts:user_list"))

        self.assertEqual(response.status_code, 403)
