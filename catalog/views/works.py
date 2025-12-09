from itertools import chain

from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DetailView, UpdateView

from catalog.forms import WorkCreateForm  # or whatever your
from catalog.models import BookSet
from catalog.models import Work
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView


class WorkCreateView(CreateView):
    model = Work
    form_class = WorkCreateForm
    success_url = reverse_lazy("work_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/work_create_partial.html"]
        return [
            "catalog/work_create_update.html"]  # normal full-page create if desired

    def form_valid(self, form):
        self.object = form.save()

        # HTMX POST → return JSON, NOT HTML
        if self.request.headers.get("HX-Request"):
            return JsonResponse(
                {"id": self.object.id, "title": self.object.title}
            )

        return redirect(self.get_success_url())

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "partials/work_create_partial.html",
                {"form": form},
                request=self.request,
            )
            return JsonResponse({"html": html}, status=400)

        return super().form_invalid(form)


class WorkCreateModalView(CreateView):
    model = Work
    form_class = WorkCreateForm

    def get_template_names(self):
        return ["partials/work_create_partial.html"]

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({"id": self.object.id, "title": self.object.title})

    def form_invalid(self, form):
        html = render_to_string(
            "partials/work_create_partial.html",
            {"form": form},
            request=self.request
        )
        return JsonResponse({"html": html}, status=400)


class WorkUpdateView(UpdateView):
    model = Work
    form_class = WorkCreateForm
    context_object_name = "work"
    template_name = "catalog/work_create_update.html"


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


def work_redirect_by_id(request, pk):
    work = get_object_or_404(Work, pk=pk)
    return redirect("work_detail", slug=work.slug)