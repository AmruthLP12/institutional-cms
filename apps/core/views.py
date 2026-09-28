"""
Core app — custom error views.
Always renders the branded 404/500 templates regardless of DEBUG setting.
"""

from django.shortcuts import render


def custom_404(request, exception=None):
    """Render the branded 404 page with full context (nav, footer, settings)."""
    return render(request, "404.html", status=404)


def custom_500(request):
    """Render the branded 500 page."""
    return render(request, "500.html", status=500)
