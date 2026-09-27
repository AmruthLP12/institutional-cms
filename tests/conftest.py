"""
Pytest configuration and reusable fixtures for Nakashara CMS tests.
"""

import pytest
from django.contrib.auth.models import Group, User
from wagtail.models import Page, Site

from apps.home.models import HomePage


@pytest.fixture
def root_page(db):
    """Return Wagtail root page."""
    return Page.get_first_root_node()


@pytest.fixture
def home_page(db, root_page):
    """Create or return HomePage."""
    home = HomePage.objects.first()
    if not home:
        Page.objects.filter(slug="home").delete()
        home = HomePage(
            title="Nakashara",
            slug="home",
            hero_headline="Pioneering Research & High-Impact Scholarship",
            intro="Nakashara is a premier public research and learning institution.",
        )
        root_page.add_child(instance=home)
        home.save_revision().publish()

    site = Site.objects.filter(is_default_site=True).first()
    if site:
        site.root_page = home
        site.save()
    else:
        Site.objects.create(
            hostname="localhost", port=8000, root_page=home, is_default_site=True
        )

    return home


@pytest.fixture
def editor_user(db):
    """Return an editor user in Content Editors group."""
    user = User.objects.create_user(username="editor", password="password123")
    group, _ = Group.objects.get_or_create(name="Content Editors")
    user.groups.add(group)
    return user


@pytest.fixture
def admin_user(db):
    """Return a superuser."""
    return User.objects.create_superuser(
        username="admin", password="password123", email="admin@example.org"
    )
