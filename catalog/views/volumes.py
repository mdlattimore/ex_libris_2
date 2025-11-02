from django.views.generic import ListView, DetailView
from catalog.models import Volume
from django.db.models.functions import Lower
from catalog.forms import VolumeForm
from django.shortcuts import render

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

def volume_create_view(request):
    form = VolumeForm(request.POST or None)
    if form.is_valid():
        volume = form.save()
        return render(request, "partials/volume_saved.html", {"volume": volume})
    return render(request, "partials/volume_form_errors.html", {"form": form})

def manual_volume_form(request):
    """Render a blank manual entry form for creating a new Volume."""
    form = VolumeForm()
    context = {"volume_form": form}
    return render(request, "partials/manual_form.html", context)