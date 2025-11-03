from django.shortcuts import render, redirect
from catalog.book_retrieval import get_book
from catalog.forms import ISBNSearchForm, VolumeForm
from pprint import pprint
from catalog.models import Author
from catalog.services.book_lookup import perform_isbn_lookup
from catalog.utils.date_parser import parse_published_date



def isbn_lookup_view(request):
    form = ISBNSearchForm(request.POST or None)
    volume_form = VolumeForm()
    result = None

    if request.method == "POST" and form.is_valid():
        isbn = form.cleaned_data["isbn"]
        result = perform_isbn_lookup(isbn)

        publication_date = parse_published_date(
            result["result"].get("published_date"))
        # Prefill form with lookup data
        initial_data = {
            "title": result["result"].get("title", ""),
            # "isbn": isbn,
            "isbn10": result["result"].get("isbn_10", ""),
            "isbn13": result["result"].get("isbn_13", ""),
            "publisher": result["result"].get("publisher", ""),
            "publication_date": publication_date,
            "publication_year": publication_date.year,
            "description": result["result"].get("description", ""),
            "works": result["work"].id if result["work"] else None,
        }
        volume_form = VolumeForm(initial=initial_data)

    context = {"form": form, "result": result, "volume_form": volume_form}

    if request.htmx:
        return render(request, "partials/lookup_result.html", context)

    return render(request, "catalog/isbn_search.html", context)