"""
Core app — template context processors.
"""


def site_context(request):
    """
    Inject global site context into every template:
    - site_settings: SiteSettings snippet
    - nav_items: top-level navigation
    - alert_banner: active emergency banner if any
    """
    context = {}

    try:
        from apps.site_settings.models import AlertBanner, NavMenuItem, SiteSettings

        site_settings = SiteSettings.for_request(request)
        context["site_settings"] = site_settings

        nav_items = (
            NavMenuItem.objects.filter(parent__isnull=True)
            .select_related("page")
            .prefetch_related("children__page")
            .order_by("order")
        )
        context["nav_items"] = nav_items

        banner = AlertBanner.objects.filter(is_active=True).first()
        context["alert_banner"] = banner

    except Exception:
        # Gracefully degrade if tables do not exist yet (pre-migration)
        context["site_settings"] = None
        context["nav_items"] = []
        context["alert_banner"] = None

    return context
