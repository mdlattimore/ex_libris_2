# catalog/forms.py
from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'collection',
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
            'status',
            'date_acquired',
            'source',
            'price',
            'acquisition_cost',
            'est_value',
            'notes',
            'binding',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'signed_by_author',
            'collectibility_notes',
            'status',
            'disposition',
            'recipient',
            'sales_price',
            'shipping_charged',
            'shipping_cost',
            'disposition_date',
            'google_info',
            'book_json'
        ]


class ISBNSearchForm(forms.Form):
    isbn = forms.CharField(max_length=13, label='ISBN')
