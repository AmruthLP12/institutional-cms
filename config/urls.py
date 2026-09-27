"""
Nakashara CMS — URL Configuration
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from apps.search import views as search_views

urlpatterns = [
    # Django admin (kept for superuser access, but Wagtail admin is primary)
    path("django-admin/", admin.site.urls),
    # Wagtail admin
    path("admin/", include(wagtailadmin_urls)),
    # Wagtail documents
    path("documents/", include(wagtaildocs_urls)),
    # Site search
    path("search/", search_views.search, name="search"),
    # Sitemap
    path("sitemap.xml", sitemap, name="sitemap"),
    # robots.txt
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots_txt",
    ),
    # Wagtail pages (must be last)
    path("", include(wagtail_urls)),
]

# Development-only additions
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
