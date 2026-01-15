from django import forms
from django.forms import modelformset_factory

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


class CoverChoiceForm(forms.Form):
    cover_image_id = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect,
        label="Cover image",
    )

    def __init__(self, *args, images=None, current_cover_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        images = images or []
        self.fields["cover_image_id"].choices = [(str(img.id), "") for img in images]
        if current_cover_id:
            self.initial["cover_image_id"] = str(current_cover_id)

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """
    An ImageField that accepts multiple uploaded files and returns a list.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # data will be either a single UploadedFile or a list of them
        if data is None:
            return []
        if isinstance(data, (list, tuple)):
            return [super().clean(d, initial) for d in data]
        return [super().clean(data, initial)]


class VolumeImageMultiUploadForm(forms.Form):
    uploads = MultipleImageField(
        required=True,
        label="Choose Image(s)",
    )








class VolumeImageEditForm(forms.ModelForm):
    class Meta:
        model = VolumeImage
        fields = ["kind", "caption"]  # hide sort_order for now

VolumeImageFormSet = modelformset_factory(
    VolumeImage,
    form=VolumeImageEditForm,
    extra=0,
    can_delete=True,
)