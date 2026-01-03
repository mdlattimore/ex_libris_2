from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, UpdateView

from catalog.forms import VolumeForm
from catalog.models import Volume, Work
from catalog.utils.normalization import normalize_sort_title



class VolumeListView(ListView):
    model = Volume
    context_object_name = "volumes"
    template_name = "catalog/volume_list.html"

    def get_queryset(self):
        return (
            Volume.objects
            .select_related("book_set")
            .prefetch_related("works__author")  # key change
        )




# class VolumeDetailView(DetailView):
#     model = Volume
#     context_object_name = "volume"
#     template_name = "catalog/volume_detail.html"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         volume = self.object
#
#         # Collect all unique genres from associated works (field is singular)
#         genres = (
#             volume.works.values_list("genre__name", flat=True)
#             .distinct()
#             .order_by("genre__name")
#         )
#
#         context["genres"] = genres
#         return context

class VolumeDetailView(DetailView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_detail.html"

    def get_queryset(self):
        # Works are used in multiple places: first_work, list of works, genres query.
        works_qs = Work.objects.select_related("author").order_by("sort_title")

        return (
            Volume.objects
            .select_related("book_set")  # keep if FK
            # If publisher is FK, add it; if CharField, omit.
            # .select_related("publisher")
            .prefetch_related(
                "collection",  # whatever your M2M related name is (you used volume.collection)
                Prefetch("works", queryset=works_qs),
                # bibliography_refs likely a reverse FK/m2m; select bibliography to avoid N+1 on ref.bibliography.code
                "bibliography_refs__bibliography",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        volume = self.object

        # If works are prefetched with genre, this becomes cheap and may not hit DB,
        # but values_list/distinct is still usually 1 DB query; that's fine.
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
