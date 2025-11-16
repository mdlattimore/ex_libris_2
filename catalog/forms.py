# catalog/forms.py
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Volume


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = [
            'title',
            'collection',
            'works',
            'book_set',
            'volume_number',
            'publisher',
            'publication_date',
            'publication_year',
            'isbn13',
            'isbn10',
            'volume_type',
            'illustrator',
            'edition',
            'description',
            'binding',
            'volume_url',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'cover_url',
            'notes',
            'acquisition_date',
            'acquisition_year',
            'source',
            'price',
            'estimated_value',
            'edition_notes',
            'volume_json',
        ]

        widgets = {
            "volume_json": JSONEditorWidget(
                options={
                    "mode": "code",  # start in "code" view
                    "modes": ["tree", "code"],
                    "search": True,
                }
            ),
        }


class ISBNSearchForm(forms.Form):
    isbn = forms.CharField(max_length=14, label='ISBN')
