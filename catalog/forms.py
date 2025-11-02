# catalog/forms.py
from django import forms
from .models import Volume


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = [
            'title',
            'works',
            'book_set',
            'volume_number',
            'publisher',
            'publication_date',
            'publication_year',
            'isbn13',
            'isbn10',
            'illustrator',
            'edition',
            'binding',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'notes',
            'acquisition_date',
            'acquisition_year',
            'source',
            'price',
            'estimated_value',
            'edition_notes'
        ]


class ISBNSearchForm(forms.Form):
    isbn = forms.CharField(max_length=14, label='ISBN')
