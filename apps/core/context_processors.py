"""
Core app — template context processors.
"""


def site_context(request):
    """
    Inject global site context into every template:
    - site_settings: SiteSettings snippet
    - nav_items: top-level navigation menu items
    - footer_groups: ordered FooterLinkGroup list with prefetched links
    - alert_banner: active emergency banner if any
    """
    context = {}

    try:
        from apps.site_settings.models import (
            AlertBanner,
            FooterLinkGroup,
            NavMenuItem,
            SiteSettings,
        )

        site_settings = SiteSettings.for_request(request)
        context["site_settings"] = site_settings

        nav_items = (
            NavMenuItem.objects.filter(parent__isnull=True, is_visible=True)
            .select_related("page")
            .prefetch_related("children__page")
            .order_by("order")
        )
        context["nav_items"] = nav_items

        footer_groups = (
            FooterLinkGroup.objects.all()
            .prefetch_related("links__page")
            .order_by("order")
        )
        context["footer_groups"] = footer_groups

        banner = AlertBanner.objects.filter(is_active=True).first()
        context["alert_banner"] = banner

    except Exception:
        # Gracefully degrade if tables do not exist yet (pre-migration)
        context["site_settings"] = None
        context["nav_items"] = []
        context["footer_groups"] = []
        context["alert_banner"] = None

    return context
