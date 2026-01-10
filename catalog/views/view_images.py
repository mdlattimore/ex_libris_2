from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from catalog.models import Volume
from catalog.forms_images import VolumeImageUploadForm

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
