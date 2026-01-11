from django import forms
from .models import VolumeImage, BooksetImage
from .utils.images.images import process_upload

class VolumeImageUploadForm(forms.ModelForm):
    upload = forms.ImageField(required=True)
    set_as_cover = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = VolumeImage
        fields = ["kind", "caption", "sort_order"]

    def __init__(self, *args, volume=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.volume = volume

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.volume = self.volume

        base, thumb, display, detail = process_upload(self.cleaned_data["upload"])

        instance.image_thumb.save(f"{base}_thumb.webp", thumb, save=False)
        instance.image_display.save(f"{base}_display.webp", display, save=False)
        instance.image_detail.save(f"{base}_detail.webp", detail, save=False)

        if commit:
            instance.save()
            if self.cleaned_data.get("set_as_cover"):
                self.volume.cover_image = instance
                self.volume.save(update_fields=["cover_image"])

        return instance


class BooksetImageUploadForm(forms.ModelForm):
    upload = forms.ImageField(required=True)
    set_as_cover = forms.BooleanField(required=False, initial=False)

    class Meta:
        model = BooksetImage
        fields = ["kind", "caption", "sort_order"]

    def __init__(self, *args, bookset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.bookset = bookset

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.bookset = self.bookset

        base, thumb, display, detail = process_upload(self.cleaned_data["upload"])

        instance.image_thumb.save(f"{base}_thumb.webp", thumb, save=False)
        instance.image_display.save(f"{base}_display.webp", display, save=False)
        instance.image_detail.save(f"{base}_detail.webp", detail, save=False)

        if commit:
            instance.save()
            if self.cleaned_data.get("set_as_cover"):
                self.bookset.cover_image = instance
                self.bookset.save(update_fields=["cover_image"])

        return instance