from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView

from catalog.forms import VolumeForm
from catalog.utils.normalization import normalize_sort_title

from django.db.models import Prefetch, F
from django.db import connection

from catalog.models import (Volume, Work, VolumeImage,
                            VolumeBibliographyReference)

# class VolumeListView(ListView):
#     model = Volume
#     context_object_name = "volumes"
#     template_name = "catalog/volume_list.html"
#
#     def get_queryset(self):
#         return (
#             Volume.objects
#             .select_related("book_set")
#             .prefetch_related("works__author")  # key change
#         )


class VolumeListView(ListView):
    model = Volume
    template_name = "catalog/volume_list.html"
    context_object_name = "volumes"
    paginate_by = 36



    def get_show_all(self):
        return "show_all" in self.request.GET

    def get_paginate_by(self, queryset):
        view = self.request.GET.get("view", "grid")
        if self.get_show_all():
            return None
        return 42 if view == "list" else 33

    SORTS = {
        "title": ["sort_title", "title", "id"],
        "date_added": ["date_added", "id"],
        "pub_year": ["publication_year", "sort_title", "id"],
        "publisher": ["publisher", "sort_title", "id"],
        "acq_date": ["acquisition_date", "sort_title", "id"],
        "status": ["status", "sort_title", "id"],
        "value": ["estimated_value", "sort_title", "id"],
        "isbn": ["isbn13", "sort_title", "id"],
    }

    DEFAULT_SORT = "title"
    DEFAULT_DIR = "asc"

    def get_queryset(self):
        # qs = super().get_queryset().select_related(
        #     "primary_work",
        #     "book_set",
        #     "cover_image",
        # ).prefetch_related(
        #     "bookshelves",
        # )

        qs = (
            super().get_queryset()
            .select_related(
                "primary_work",
                "book_set",
                "cover_image",
                # add this ONLY if Work.author is FK:
                "primary_work__author",
            )
            # drop bookshelves if you don't display them:
            # .prefetch_related("bookshelves")
            .defer("notes", "edition_notes", "description", "volume_json")
        )

        sort = self.request.GET.get("sort", self.DEFAULT_SORT)
        direction = self.request.GET.get("dir", self.DEFAULT_DIR)

        if sort not in self.SORTS:
            sort = self.DEFAULT_SORT
        if direction not in ("asc", "desc"):
            direction = self.DEFAULT_DIR

        self.sort = sort
        self.direction = direction

        fields = self.SORTS[sort]
        nulls_last_fields = {"pub_year", "acq_date", "value", "isbn",
            "publisher"}
        use_nulls_last = sort in nulls_last_fields

        supports_nulls_ordering = getattr(connection.features,
                                          "supports_nulls_ordering", False)

        order_by = []
        for field in fields:
            expr = F(field)
            if use_nulls_last and supports_nulls_ordering:
                expr = expr.asc(nulls_last=True) if direction == "asc" else expr.desc(nulls_last=True)
            else:
                expr = expr.asc() if direction == "asc" else expr.desc()
            order_by.append(expr)


        return qs.order_by(*order_by)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["sort"] = getattr(self, "sort", self.DEFAULT_SORT)
        ctx["dir"] = getattr(self, "direction", self.DEFAULT_DIR)
        ctx["show_all"] = self.get_show_all()

        view = self.request.GET.get("view", "grid")
        if view not in ("grid", "list"):
            view = "grid"
        ctx["view"] = view

        return ctx







class VolumeDetailView(DetailView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_detail.html"

    def get_queryset(self):
        works_qs = (
            Work.objects
            .select_related("author")
            .prefetch_related("genre")      # <-- key change
            .order_by("sort_title")
        )

        images_qs = (
            VolumeImage.objects
            .only(
                "id", "volume_id", "kind", "caption", "sort_order",
                "image_thumb", "image_display", "image_detail", "created_at")
            .order_by("sort_order", "created_at")
        )

        refs_qs = VolumeBibliographyReference.objects.select_related("bibliography")

        return (
            Volume.objects
            .select_related(
                "book_set",
                "cover_image",
                "primary_work",
                "primary_work__author",
            )
            .prefetch_related(
                "bookshelves",
                Prefetch("works", queryset=works_qs),
                Prefetch("images", queryset=images_qs),
                Prefetch("bibliography_refs", queryset=refs_qs),
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volume = self.object

        # Zero extra DB hits (because works + works.genres are prefetched)
        genres = []
        seen = set()
        for w in volume.works.all():
            for g in w.genre.all():
                if g.name not in seen:
                    seen.add(g.name)
                    genres.append(g.name)
        genres.sort(key=str.casefold)

        context["genres"] = genres

        imgs = list(volume.images.all())  # uses prefetch if you set it up
        cover_id = volume.cover_image_id

        # cover first, preserve relative order of the rest
        if cover_id:
            imgs.sort(key=lambda im: 0 if im.id == cover_id else 1)

        context["ordered_images"] = imgs
        context[
            "cover_slide_index"] = 0 if cover_id else 0  # cover will be 0 when present
        print(context["ordered_images"])
        return context



class VolumeUpdateView(LoginRequiredMixin, UpdateView):
    model = Volume
    context_object_name = "volume"
    form_class = VolumeForm
    template_name = "catalog/volume_update.html"


    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     return form



def volume_create_view(request):
    form = VolumeForm(request.POST or None)
    if form.is_valid():
        volume = form.save()
        return render(request, "partials/volume_saved.html", {"volume": volume})
    return render(request, "partials/volume_form_errors.html", {"form": form})

@login_required
def manual_volume_form(request):
    """Render a blank manual entry form for creating a new Volume."""
    form = VolumeForm()
    context = {"volume_form": form}
    return render(request, "partials/manual_form.html", context)


def volume_redirect_by_id(request, pk):
    vol = get_object_or_404(Volume, pk=pk)
    return redirect("volume_detail", slug=vol.slug)
