from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from catalog.models import Bookshelf, Volume, Work


class BookshelfCreateView(LoginRequiredMixin, CreateView):
    model = Bookshelf
    context_object_name = "bookshelf"
    template_name = "catalog/bookshelf_create_update.html"
    fields = "__all__"


class BookshelfUpdateView(LoginRequiredMixin, UpdateView):
    model = Bookshelf
    context_object_name = "bookshelf"
    template_name = "catalog/bookshelf_create_update.html"
    fields = "__all__"


# class CollectionListView(ListView):
#     model = Collection
#     context_object_name = 'collections'
#     template_name = "catalog/bookshelf_list.html"
#
#     def get_queryset(self):
#         return Collection.objects.all().order_by('name')


class BookshelfListView(ListView):
    model = Bookshelf
    context_object_name = "bookshelves"
    template_name = "catalog/bookshelf_list.html"

    def get_queryset(self):
        return(
            Bookshelf.objects
            .prefetch_related("volumes")
        ).order_by("name")

# class CollectionDetailView(DetailView):
#     model = Collection
#     context_object_name = 'collection'
#     template_name = "catalog/bookshelf_detail.html"

class BookshelfDetailView(DetailView):
    model = Bookshelf
    context_object_name = "bookshelf"
    template_name = "catalog/bookshelf_detail.html"

    def get_queryset(self):
        works_qs = Work.objects.select_related("author").order_by("sort_title")

        volumes_qs = (
            Volume.objects
            .order_by("sort_title")
            .prefetch_related(Prefetch("works", queryset=works_qs))
        )

        return Bookshelf.objects.prefetch_related(
            Prefetch("volumes", queryset=volumes_qs)
        )


def bookshelf_redirect_by_id(request, pk):
    bookshelf = get_object_or_404(Bookshelf, pk=pk)
    return redirect("bookshelf_detail", slug=bookshelf.slug)
