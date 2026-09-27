"""
Management command to create standard institutional Wagtail/Django permission groups.
Idempotent — safe to run multiple times.
"""

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from wagtail.models import GroupPagePermission, Page


class Command(BaseCommand):
    help = "Sets up standard Wagtail & Django permission groups for the institution."

    GROUPS = [
        "Administrators",
        "Content Editors",
        "Content Publishers",
        "Policy Editors",
        "Document Managers",
        "News Editors",
        "Events Editors",
        "Reviewers",
    ]

    def handle(self, *args, **options):
        root_page = Page.get_first_root_node()

        for group_name in self.GROUPS:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group: {group_name}"))
            else:
                self.stdout.write(f"Group already exists: {group_name}")

            # Assign Wagtail page permissions if root page exists
            if root_page:
                if group_name in ["Administrators", "Content Publishers"]:
                    codenames = [
                        "add_page",
                        "change_page",
                        "publish_page",
                        "lock_page",
                        "unlock_page",
                    ]
                elif group_name in [
                    "Content Editors",
                    "Policy Editors",
                    "News Editors",
                    "Events Editors",
                ]:
                    codenames = ["add_page", "change_page"]
                else:
                    codenames = []

                for codename in codenames:
                    try:
                        perm = Permission.objects.get(
                            content_type__app_label="wagtailcore",
                            codename=codename,
                        )
                        GroupPagePermission.objects.get_or_create(
                            group=group,
                            page=root_page,
                            permission=perm,
                        )
                    except Permission.DoesNotExist:
                        pass

        self.stdout.write(
            self.style.SUCCESS(
                "All institutional groups and permissions configured successfully."
            )
        )
