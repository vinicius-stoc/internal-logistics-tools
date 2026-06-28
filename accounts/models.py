from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    must_change_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("access_dashboard", "Can access dashboard"),
            ("manage_internal_users", "Can manage internal users"),
            ("view_import_history", "Can view import history"),
            ("reset_internal_user_password", "Can reset internal user password"),
            ("export_dashboard", "Can export dashboard"),
        ]

    def __str__(self):
        return f"Profile for {self.user.get_username()}"
