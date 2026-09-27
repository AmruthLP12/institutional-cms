import pytest

from apps.legal.models import LegalIndexPage, LegalPage


@pytest.mark.django_db
class TestLegalPolicyPages:
    def test_approved_policy_is_accessible(self, client, home_page):
        legal_index = LegalIndexPage(title="Policies", slug="policies")
        home_page.add_child(instance=legal_index)
        legal_index.save_revision().publish()

        policy = LegalPage(
            title="Privacy Policy",
            slug="privacy-policy",
            policy_type=LegalPage.PolicyType.PRIVACY,
            approval_status=LegalPage.ApprovalStatus.PUBLISHED,
            version="1.0",
            summary="<p>Official privacy policy</p>",
        )
        legal_index.add_child(instance=policy)
        policy.save_revision().publish()

        response = client.get("/policies/privacy-policy/")
        assert response.status_code == 200
        assert "Privacy Policy" in response.content.decode()

    def test_unapproved_policy_is_hidden_even_when_live(self, client, home_page):
        """
        Critical requirement: CMS publication does not equal legal approval.
        A page live in Wagtail with approval_status != 'published' must return 404.
        """
        legal_index = LegalIndexPage(title="Policies", slug="policies")
        home_page.add_child(instance=legal_index)
        legal_index.save_revision().publish()

        policy = LegalPage(
            title="Draft Policy",
            slug="draft-policy",
            policy_type=LegalPage.PolicyType.INSTITUTIONAL,
            approval_status=LegalPage.ApprovalStatus.DRAFT,
            version="0.1",
        )
        legal_index.add_child(instance=policy)
        policy.save_revision().publish()

        response = client.get("/policies/draft-policy/")
        assert response.status_code == 404

    def test_legal_index_groups_only_published_policies(self, client, home_page):
        legal_index = LegalIndexPage(title="Policies", slug="policies")
        home_page.add_child(instance=legal_index)
        legal_index.save_revision().publish()

        # 1 Published, 1 Draft
        p1 = LegalPage(
            title="Published Policy",
            slug="published-policy",
            policy_type=LegalPage.PolicyType.ACCESSIBILITY,
            approval_status=LegalPage.ApprovalStatus.PUBLISHED,
        )
        legal_index.add_child(instance=p1)
        p1.save_revision().publish()

        p2 = LegalPage(
            title="Under Review Policy",
            slug="review-policy",
            policy_type=LegalPage.PolicyType.ACCESSIBILITY,
            approval_status=LegalPage.ApprovalStatus.UNDER_REVIEW,
        )
        legal_index.add_child(instance=p2)
        p2.save_revision().publish()

        response = client.get("/policies/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Published Policy" in content
        assert "Under Review Policy" not in content
