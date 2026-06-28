from django.core.management.base import BaseCommand

from accounts.services.rbac_service import GROUP_PERMISSIONS, setup_rbac


class Command(BaseCommand):
    help = "Create or update internal RBAC groups and permissions."

    def handle(self, *args, **options):
        result = setup_rbac()

        self.stdout.write(self.style.SUCCESS("RBAC setup completed."))
        self.stdout.write(f"Permissions: {len(result['permissions'])}")
        self.stdout.write(f"Groups: {', '.join(GROUP_PERMISSIONS.keys())}")
        self.stdout.write(f"User profiles created: {result['created_profiles']}")
