import re

from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from catalog.models import Work, BookSet
from itertools import chain
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView
from catalog.forms import WorkCreateForm
from django.shortcuts import redirect


# class WorkCreateView(CreateView):
#     model = Work
#     context_object_name = "work"
#     template_name = "catalog/work_create_update.html"
#     fields = "__all__"

from django.views.generic import CreateView
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.template.loader import render_to_string

from catalog.models import Work, Author
from catalog.forms import WorkCreateForm, AuthorCreateForm  # or whatever your
# forms are called


class WorkCreateView(CreateView):
    model = Work
    form_class = WorkCreateForm
    success_url = reverse_lazy("work_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/work_create_partial.html"]
        return ["catalog/work_create_update.html"]  # normal full-page create if desired

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



# class WorkCreateModalView(View):
#     template_name = "modals/work_form_modal.html"
#
#     def post(self, request, *args, **kwargs):
#         form = WorkCreateForm(request.POST)
#         if form.is_valid():
#             work = form.save()
#
#             # Render the new option for the select field with out-of-band swap
#             option_html = render_to_string(
#                 "partials/work_option.html",
#                 {"work": work},
#                 request=request
#             )
#
#             return HttpResponse(option_html)
#
#         # If form is not valid, re-render the modal with errors
#         html = render_to_string(self.template_name, {"form": form}, request=request)
#         return HttpResponse(html)

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