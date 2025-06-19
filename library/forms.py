# library/forms.py
from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'subtitle',
            'author',
            'publisher',
            'publication_date',
            'number_of_pages',
            'isbn_10',
            'isbn_13',
            'genres',
            'cover_id',
            'owned',
            'date_acquired',
            'source',
            'price',
            'est_value',
            'notes',
            'binding',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'signed_by_author',
            'is_collectible',
            'collectible_notes',
            'google_info',
            'book_json'
        ]


class ISBNSearchForm(forms.Form):
    isbn = forms.CharField(max_length=13, label='ISBN')
