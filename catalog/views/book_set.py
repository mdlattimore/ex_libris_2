from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView

from catalog.models import BookSet
from catalog.utils.normalization import normalize_sort_title
from catalog.views import CatalogBaseView


class BookSetListView(CatalogBaseView):
    model = BookSet
    context_object_name = 'booksets'
    template_name = "catalog/work_list.html"
    view_type = "booksets"

    def get_context_data(self, **kwargs):
        context = super(BookSetListView, self).get_context_data(**kwargs)
        context["booksets_sorted"] = BookSet.objects.all().order_by(
            normalize_sort_title('title'))
        return context


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
