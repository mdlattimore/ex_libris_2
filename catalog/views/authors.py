from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, CreateView, UpdateView
from django.views.generic import ListView

from catalog.forms import AuthorCreateForm
from catalog.models import Author, Work, Volume


class AuthorCreateView(LoginRequiredMixin, CreateView):
    model = Author
    form_class = AuthorCreateForm
    success_url = reverse_lazy("author_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/author_create_partial.html"]
        return ["catalog/author_create_update.html"]

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request"):
            return JsonResponse({
                "id": self.object.id,
                "name": self.object.full_name
            })
        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "partials/author_create_partial.html",
                {"form": form},
                request=self.request
            )
            return JsonResponse({"html": html}, status=400)
        return super().form_invalid(form)


class AuthorCreateModalView(View):
    template_name = "modals/author_form_modal.html"

    def get(self, request, *args, **kwargs):
        form = AuthorCreateForm()
        html = render_to_string(self.template_name, {"form": form},
                                request=request)
        return HttpResponse(html)

    def post(self, request, *args, **kwargs):
        form = AuthorCreateForm(request.POST)
        if form.is_valid():
            author = form.save()

            # Return out-of-band option snippet
            option_html = render_to_string(
                "partials/author_option.html",
                {"author": author},
                request=request,
            )
            return HttpResponse(option_html)

        html = render_to_string(self.template_name, {"form": form},
                                request=request)
        return HttpResponse(html)


class AuthorUpdateView(LoginRequiredMixin, UpdateView):
    model = Author
    context_object_name = "author"
    form_class = AuthorCreateForm
    template_name = "catalog/author_create_update.html"


# class AuthorListView(ListView):
#     model = Author
#     context_object_name = "authors"
#     template_name = "catalog/author_list.html"
#
#     def get_queryset(self):
#         """
#         Prefetch works and volumes so the template doesn't hit the database
#         repeatedly, and attach unique_volumes to each author.
#         """
#         qs = (
#             Author.objects
#             .prefetch_related(
#                 Prefetch(
#                     "works",
#                     queryset=Work.objects.prefetch_related("volumes")
#                 )
#             )
#         )
#
#         # Attach deduplicated volume list to each author
#         for author in qs:
#             seen = set()
#             unique_volumes = []
#             for work in author.works.all():
#                 for vol in work.volumes.all():
#                     if vol.pk not in seen:
#                         seen.add(vol.pk)
#                         unique_volumes.append(vol)
#             author.unique_volumes = unique_volumes
#
#         return qs
#
#     def get_context_data(self, **kwargs):
#         """
#         Preserve your existing sorting by sort_name
#         and expose authors as authors_display.
#         """
#         context = super().get_context_data(**kwargs)
#
#         authors_sorted = sorted(
#             self.object_list, key=lambda author: author.sort_name
#         )
#         context["authors_display"] = authors_sorted
#
#         return context

class AuthorListView(ListView):
    model = Author
    context_object_name = "authors"
    template_name = "catalog/author_list.html"

    def get_queryset(self):
        volumes_qs = (
            Volume.objects
            .select_related("cover_image")  # avoid N+1 if template calls vol.cover_src
            .order_by("sort_title")
        )

        works_qs = (
            Work.objects
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
            .order_by("sort_title")
        )

        return (
            Author.objects
            .prefetch_related(Prefetch("works", queryset=works_qs))
            .order_by("sort_name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # If you're already ordering by sort_name in the queryset,
        # you don't need to sort again here.
        authors = list(context["authors"])

        for author in authors:
            seen = set()
            unique_vols = []
            for work in author.works.all():        # prefetched
                for vol in work.volumes.all():     # prefetched
                    if vol.pk not in seen:
                        seen.add(vol.pk)
                        unique_vols.append(vol)
            author.unique_volumes = unique_vols

        context["authors_display"] = authors
        return context

class AuthorDetailView(DetailView):
    model = Author
    context_object_name = 'author'
    template_name = "catalog/author_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object

        # Keep your existing works logic (whatever it is)
        context["works"] = author.works.all().order_by("first_published")  #
        # adjust field

        # Add volumes linked to any of the author's works
        context["volumes"] = (
            Volume.objects
            .filter(works__author=author)
            .distinct()
            .order_by("sort_title")  # adjust if you sort differently
        )
        return context


def author_redirect_by_id(request, pk):
    vol = get_object_or_404(Author, pk=pk)
    return redirect("volume_detail", slug=vol.slug)
