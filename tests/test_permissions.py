import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.mark.django_db
class TestPermissions:
    def test_setup_groups_command(self):
        call_command("setup_groups")

        expected_groups = [
            "Administrators",
            "Content Editors",
            "Content Publishers",
            "Policy Editors",
            "Document Managers",
            "News Editors",
            "Events Editors",
            "Reviewers",
        ]
        for name in expected_groups:
            assert Group.objects.filter(name=name).exists()
