from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView
from catalog.models import BookSet
from catalog.forms_images import BooksetImageUploadForm

class BooksetImageUploadView(LoginRequiredMixin, FormView):
    template_name = "catalog/bookset_image_upload.html"
    form_class = BooksetImageUploadForm

    def dispatch(self, request, *args, **kwargs):
        self.bookset = get_object_or_404(BookSet, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        kw["bookset"] = self.bookset
        return kw

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return self.bookset.get_absolute_url()
