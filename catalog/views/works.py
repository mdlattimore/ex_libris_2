from itertools import chain

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic import DetailView, UpdateView

from catalog.forms import WorkCreateForm  # or whatever your
from catalog.models import BookSet
from catalog.models import Work, Volume
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView
from django.db.models import Prefetch


class WorkCreateView(LoginRequiredMixin, CreateView):
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



from itertools import chain

# class WorkListView(CatalogBaseView):
#     model = Work
#     context_object_name = "items"
#     template_name = "catalog/work_list.html"
#     view_type = "works"
#
#     def get_queryset(self):
#         volumes_qs = Volume.objects.only("id", "title", "cover_url", "slug")
#
#         works = (
#             Work.objects
#             .select_related("author")
#             .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
#         )
#
#         booksets = (
#             BookSet.objects
#             .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
#         )
#
#         combined = chain(works, booksets)
#         return sorted(combined, key=lambda obj: normalize_sort_title(obj.title))

# class WorkListView(CatalogBaseView):
#     model = Work
#     template_name = "catalog/work_list.html"
#     view_type = "works"
#
#     def get_queryset(self):
#         volumes_qs = Volume.objects.only("id", "title", "cover_url", "slug",
#                                          "cover_image")
#         return (
#             Work.objects
#             .select_related("author")
#             .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
#             .order_by("sort_title")
#         )

class WorkListView(CatalogBaseView):
    model = Work
    template_name = "catalog/work_list.html"
    context_object_name = "items"

    def get_queryset(self):
        volumes_qs = (
            Volume.objects
            .select_related("cover_image")  # <-- kills the 187 VolumeImage queries
            .only(
                "id", "slug", "title", "sort_title",
                "cover_url", "cover_image_id",
                "cover_image__id",                # safe
                "cover_image__image_display",     # so .url doesn't trigger extra work
                "cover_image__image_thumb",       # if you ever switch to thumb here
            )
            .order_by("sort_title")
        )

        return (
            Work.objects
            .select_related("author")
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
            .order_by("sort_title")
        )


class WorkDetailView(DetailView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_detail.html"


def work_redirect_by_id(request, pk):
    work = get_object_or_404(Work, pk=pk)
    return redirect("work_detail", slug=work.slug)
