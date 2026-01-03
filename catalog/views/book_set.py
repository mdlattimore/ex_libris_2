from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView

from catalog.models import BookSet, Volume
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView


# class BookSetListView(CatalogBaseView):
#     model = BookSet
#     template_name = "catalog/work_list.html"
#     view_type = "booksets"
#
#     # def get_queryset(self):
#     #     return BookSet.objects.all().order_by("title")
#
#     def get_queryset(self):
#         qs = (
#             BookSet.objects
#             .all()
#             .prefetch_related(
#                 "volumes")  # kills the per-bookset volumes queries
#             .order_by("title")
#         )
#
#         # If BookSet.author is a ForeignKey, this prevents an N+1 on {{ item.author }}.
#         # If it's not (e.g., CharField), Django will raise, so we safely try it.
#         try:
#             qs = qs.select_related("author")
#         except Exception:
#             pass
#
#         return qs

from django.db.models import Prefetch
from catalog.models import BookSet, Volume, Work  # adjust import path if needed

class BookSetListView(CatalogBaseView):
    model = BookSet
    template_name = "catalog/work_list.html"
    view_type = "booksets"

    def get_queryset(self):
        # We render volume cover thumbnails in the list,
        # so we must prefetch volumes to kill the N+1.
        volumes_qs = Volume.objects.order_by("sort_title")

        # If your BookSet.author display is computed via volumes -> works -> author,
        # prefetch those too. This costs 1 extra query but prevents per-row queries
        # if `item.author` walks relations.
        works_qs = Work.objects.select_related("author").order_by("sort_title")
        volumes_qs = volumes_qs.prefetch_related(Prefetch("works", queryset=works_qs))

        return (
            BookSet.objects
            .all()
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
            .order_by("title")
        )


from django.db.models import Prefetch

# class BookSetListView(CatalogBaseView):
#     model = BookSet
#     template_name = "catalog/work_list.html"
#     view_type = "booksets"
#
#     def get_queryset(self):
#         volumes_qs = Volume.objects.only("id", "title", "cover_url", "slug")
#         return (
#             BookSet.objects
#             .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
#             .order_by("title")
#         )



class BookSetDetailView(DetailView):
    model = BookSet
    context_object_name = 'bookset'
    template_name = "catalog/bookset_detail.html"

    def get_context_data(self, **kwargs):
        context = super(BookSetDetailView, self).get_context_data(**kwargs)
        context["sorted_bookset"] = self.object.volumes.order_by(
            'volume_number', normalize_sort_title('title'))
        return context


def bookset_redirect_by_id(request, pk):
    bookset = get_object_or_404(BookSet, pk=pk)
    return redirect("bookset_detail", slug=bookset.slug)
