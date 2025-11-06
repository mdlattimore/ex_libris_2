from django.views.generic import ListView, DetailView
from catalog.models import Collection


class CollectionListView(ListView):
    model = Collection
    context_object_name = 'collections'
    template_name = "catalog/collection_list.html"


class CollectionDetailView(DetailView):
    model = Collection
    context_object_name = 'collection'
    template_name = "catalog/collection_detail.html"
