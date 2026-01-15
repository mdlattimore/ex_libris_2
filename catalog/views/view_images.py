from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import FormView
from catalog.models import Volume, VolumeImage
from catalog.forms_images import VolumeImageUploadForm, \
    VolumeImageMultiUploadForm, VolumeImageFormSet, CoverChoiceForm
from catalog.services.images import ingest_volume_images


class VolumeImageUploadView(LoginRequiredMixin, FormView):
    template_name = "catalog/volume_image_upload.html"
    form_class = VolumeImageUploadForm

    def dispatch(self, request, *args, **kwargs):
        self.volume = get_object_or_404(Volume, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["volume"] = self.volume
        return kw

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.volume.get_absolute_url()



class VolumeImageManageView(LoginRequiredMixin, View):
    template_name = "catalog/volume_image_manage.html"

    def dispatch(self, request, *args, **kwargs):
        self.volume = get_object_or_404(Volume, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # IMPORTANT: must return a QuerySet (not a list)
        return VolumeImage.objects.filter(volume=self.volume).order_by("sort_order", "created_at")

    def get(self, request, *args, **kwargs):
        qs = self.get_queryset()
        upload_form = VolumeImageMultiUploadForm()
        formset = VolumeImageFormSet(queryset=qs)

        return render(request, self.template_name, {
            "volume": self.volume,
            "upload_form": upload_form,
            "formset": formset,
        })

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "upload":
            upload_form = VolumeImageMultiUploadForm(request.POST, request.FILES)
            formset = VolumeImageFormSet(queryset=self.get_queryset())

            if upload_form.is_valid():
                files = upload_form.cleaned_data["uploads"]  # list of uploaded files
                ingest_volume_images(
                    volume=self.volume,
                    files=files,
                    set_first_as_cover=False,  # cover handled via radios on save step
                )
                return redirect(request.path)

            return render(request, self.template_name, {
                "volume": self.volume,
                "upload_form": upload_form,
                "formset": formset,
            })

        # Default: action == "save" (or missing)
        qs = self.get_queryset()
        formset = VolumeImageFormSet(request.POST, queryset=qs)
        upload_form = VolumeImageMultiUploadForm()

        if formset.is_valid():
            # Save edits (kind/caption)
            instances = formset.save(commit=False)
            for inst in instances:
                inst.volume = self.volume  # defensive
                inst.save()

            # Handle deletions
            deleted_ids = {obj.id for obj in formset.deleted_objects}
            for obj in formset.deleted_objects:
                obj.delete()

            # Set cover (only if not deleted). Radio is rendered per-card in template.
            chosen = request.POST.get("cover_image_id")  # string or None/"" if "no cover"
            if chosen:
                chosen_id = int(chosen)
                if chosen_id in deleted_ids:
                    self.volume.cover_image = None
                else:
                    self.volume.cover_image_id = chosen_id
            else:
                # allow "no cover"
                self.volume.cover_image = None

            self.volume.save(update_fields=["cover_image"])
            return redirect(self.volume.get_absolute_url())

        return render(request, self.template_name, {
            "volume": self.volume,
            "upload_form": upload_form,
            "formset": formset,
        })