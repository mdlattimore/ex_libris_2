from django.views.generic import ListView, DetailView
from catalog.models import Work, BookSet
from itertools import chain


class WorkListView(ListView):
    model = Work
    context_object_name = "items"
    template_name = "catalog/work_list.html"

    def get_queryset(self):
        """
        Combine Work and BookSet objects into one unified queryset,
        sorted alphabetically by title.
        """
        works = Work.objects.all().prefetch_related("volumes")
        booksets = BookSet.objects.all().prefetch_related("volumes")

        # Combine and sort
        combined = chain(works, booksets)
        sorted_combined = sorted(combined, key=lambda obj: obj.title.lower())

        return sorted_combined

    def get_context_data(self, **kwargs):
        """
        Override to ensure the template context variable name matches expectations.
        """
        context = super().get_context_data(**kwargs)
        context["works"] = self.get_queryset()
        return context


class WorkDetailView(DetailView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_detail.html"