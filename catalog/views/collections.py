from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from catalog.models import Collection, Volume, Work


class CollectionCreateView(CreateView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_create_update.html"
    fields = "__all__"


class CollectionUpdateView(UpdateView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_create_update.html"
    fields = "__all__"


# class CollectionListView(ListView):
#     model = Collection
#     context_object_name = 'collections'
#     template_name = "catalog/collection_list.html"
#
#     def get_queryset(self):
#         return Collection.objects.all().order_by('name')


class CollectionListView(ListView):
    model = Collection
    context_object_name = "collections"
    template_name = "catalog/collection_list.html"

    def get_queryset(self):
        return(
            Collection.objects
            .prefetch_related("volumes")
        ).order_by("name")

# class CollectionDetailView(DetailView):
#     model = Collection
#     context_object_name = 'collection'
#     template_name = "catalog/collection_detail.html"

class CollectionDetailView(DetailView):
    model = Collection
    context_object_name = "collection"
    template_name = "catalog/collection_detail.html"

    def get_queryset(self):
        works_qs = Work.objects.select_related("author").order_by("sort_title")

        volumes_qs = (
            Volume.objects
            .order_by("sort_title")
            .prefetch_related(Prefetch("works", queryset=works_qs))
        )

        return Collection.objects.prefetch_related(
            Prefetch("volumes", queryset=volumes_qs)
        )


def collection_redirect_by_id(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    return redirect("collection_detail", slug=collection.slug)
