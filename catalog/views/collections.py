from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from catalog.models import Collection, Volume, Work


class CollectionCreateView(LoginRequiredMixin, CreateView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_create_update.html"
    fields = "__all__"


class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_create_update.html"
    fields = "__all__"


class CollectionListView(ListView):
    model = Collection
    context_object_name = "collections"
    template_name = "catalog/collection_list.html"

    def get_queryset(self):
        return (
            Collection.objects
            .prefetch_related("works")
        ).order_by("name")


class CollectionDetailView(DetailView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_detail.html"

    def get_queryset(self):
        volumes_qs = (
            Volume.objects
            .select_related("cover_image", "book_set", "primary_work")
            .order_by("sort_title")
        )

        works_qs = (
            Work.objects
            .select_related("author")
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
            .order_by("sort_title")
        )

        return Collection.objects.prefetch_related(
            Prefetch("works", queryset=works_qs)
        )
