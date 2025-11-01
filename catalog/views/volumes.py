from django.views.generic import ListView, DetailView
from catalog.models import Volume
from django.db.models.functions import Lower


class VolumeListView(ListView):
    model = Volume
    context_object_name = 'volumes'
    template_name = "catalog/volume_list.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["volumes_display"] = Volume.objects.order_by(Lower("title"))
    #     return context
    def get_queryset(self):
        # Include related BoxSet to avoid extra queries
        qs = (
            Volume.objects.select_related("book_set")
            .order_by(
                Lower("book_set__title"),  # sort by set name (nulls first)
                Lower("title"),  # then by volume title
            )
        )
        return qs


class VolumeDetailView(DetailView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_detail.html"