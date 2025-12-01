import re

from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from catalog.models import Work, BookSet
from itertools import chain
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView
from catalog.forms import WorkCreateForm
from django.shortcuts import redirect


class WorkCreateView(CreateView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_create_update.html"
    fields = "__all__"


class WorkCreateModalView(CreateView):
    model = Work
    form_class = WorkCreateForm

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/work_create_partial.html"]
        return ["catalog/work_create_update.html"]

    def form_valid(self, form):
        self.object = form.save()

        if self.request.headers.get("HX-Request"):
            return JsonResponse({"id": self.object.id, "title": self.object.title})

        return redirect(self.object.get_absolute_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))



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