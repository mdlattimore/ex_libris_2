from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView

from catalog.forms import VolumeForm
from catalog.models import Volume
from catalog.utils.normalization import normalize_sort_title


class VolumeListView(ListView):
    model = Volume
    context_object_name = 'volumes'
    template_name = "catalog/volume_list.html"

    def get_queryset(self):
        qs = Volume.objects.select_related("book_set")
        return sorted(qs, key=lambda v: normalize_sort_title(v.title))


class VolumeDetailView(DetailView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volume = self.object

        # Collect all unique genres from associated works (field is singular)
        genres = (
            volume.works.values_list("genre__name", flat=True)
            .distinct()
            .order_by("genre__name")
        )

        context["genres"] = genres
        return context


class VolumeUpdateView(UpdateView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_update.html"
    fields = "__all__"
    exclude_fields = ("volume_json",)

    # def get_form(self, form_class=None):
    #     form = super().get_form(form_class)
    #     return form


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


def volume_redirect_by_id(request, pk):
    vol = get_object_or_404(Volume, pk=pk)
    return redirect("volume_detail", slug=vol.slug)
