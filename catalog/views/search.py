from django.views.generic import TemplateView
from django.db.models import Q
from catalog.models import Author, Work, Volume, BookSet


class SearchResultsView(TemplateView):
    template_name = "catalog/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get("q", "").strip()
        context["query"] = q

        if not q:
            # Empty search → return nothing but still render page
            context.update({
                "authors": [],
                "works": [],
                "booksets": [],
                "volumes": [],
            })
            return context

        # --- AUTHORS ---
        authors = Author.objects.filter(
            Q(full_name__icontains=q) |
            Q(bio__icontains=q)  # if you have such a field
        ).order_by("sort_name")

        # --- WORKS ---
        works = Work.objects.filter(
            Q(title__icontains=q) |
            Q(author__full_name__icontains=q) |
            Q(notes__icontains=q) |
            Q(genre__name__icontains=q) |
            Q(work_type__icontains=q)
        ).select_related("author").distinct().order_by("sort_title")

        # --- BOOKSETS ---
        booksets = (
            BookSet.objects.filter(
                Q(title__icontains=q)
                | Q(illustrator__icontains=q)  # if this exists
                | Q(volumes__title__icontains=q)
                | Q(volumes__works__title__icontains=q)
                | Q(volumes__works__author__full_name__icontains=q)
            )
            .distinct()
            .order_by("sort_title")  # or "title" if you don’t have sort_title
        )

        # --- VOLUMES ---
        volumes = Volume.objects.filter(
            Q(title__icontains=q) |
            Q(works__title__icontains=q) |
            Q(works__author__full_name__icontains=q) |
            Q(works__genre__name__icontains=q)
        ).select_related("book_set").prefetch_related("works").distinct().order_by("sort_title")

        context.update({
            "authors": authors,
            "works": works,
            "booksets": booksets,
            "volumes": volumes,
        })
        return context
