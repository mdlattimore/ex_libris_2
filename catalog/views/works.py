import re

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from catalog.models import Work, BookSet
from itertools import chain
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView


class WorkCreateView(CreateView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_create_update.html"
    fields = "__all__"


class WorkUpdateView(UpdateView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_create_update.html"
    fields = "__all__"


class WorkListView(CatalogBaseView):
    model = Work
    context_object_name = "items"
    template_name = "catalog/work_list.html"
    view_type = "works"

    def get_queryset(self):
        """
        Combine Work and BookSet objects into one unified queryset,
        sorted alphabetically by title (ignoring leading articles).
        """
        works = Work.objects.all().prefetch_related("volumes")
        booksets = BookSet.objects.all().prefetch_related("volumes")

        combined = chain(works, booksets)
        sorted_combined = sorted(
            combined,
            key=lambda obj: normalize_sort_title(obj.title)
        )

        return sorted_combined

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["works"] = self.get_queryset()
        return context


class WorkDetailView(DetailView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_detail.html"