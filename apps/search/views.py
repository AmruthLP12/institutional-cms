from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page


def search(request):
    search_query = request.GET.get("query", None)
    page = request.GET.get("page", 1)

    # Search
    if search_query:
        # Search live, public pages, excluding private ones
        search_results = Page.objects.live().public().search(search_query)
        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    template = "search/search.html"
    if request.headers.get("HX-Request"):
        template = "search/includes/search_results.html"

    return render(
        request,
        template,
        {
            "search_query": search_query,
            "search_results": search_results,
        },
    )
