from django.views.generic import ListView, DetailView
from catalog.models import BookSet
from catalog.utils.normalization import normalize_sort_title


class BookSetListView(ListView):
    model = BookSet
    context_object_name = 'booksets'
    template_name = "catalog/bookset_list.html"

    def get_context_data(self, **kwargs):
        context = super(BookSetListView, self).get_context_data(**kwargs)
        context["booksets_sorted"] = BookSet.objects.all().order_by(
            normalize_sort_title('title'))
        return context


class BookSetDetailView(DetailView):
    model = BookSet
    context_object_name = 'bookset'
    template_name = "catalog/bookset_detail.html"