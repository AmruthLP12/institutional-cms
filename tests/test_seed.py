import pytest
from django.core.management import call_command

from apps.legal.models import LegalPage


@pytest.mark.django_db
class TestSeedCommand:
    def test_seed_cms_runs_idempotently(self):
        # Run seed once
        call_command("seed_cms", demo=True, legal=True, navigation=True)
        count_policies_1 = LegalPage.objects.count()
        assert count_policies_1 >= 5

        # Run seed a second time — must not create duplicates
        call_command("seed_cms", demo=True, legal=True, navigation=True)
        count_policies_2 = LegalPage.objects.count()
        assert count_policies_1 == count_policies_2
