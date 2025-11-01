from django.shortcuts import render, redirect
from catalog.book_retrieval import get_book
from catalog.forms import ISBNSearchForm
from pprint import pprint
from catalog.models import Author
from catalog.services.book_lookup import perform_isbn_lookup


def isbn_lookup(request):
    result = None
    if request.method == "POST":
        form = ISBNSearchForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['isbn']
            print("view", isbn)
            try:
                result = perform_isbn_lookup(isbn)
                print("View result", result)
            except:
                result = {"none_found": "None found"}
            pprint(result)



    else:
        form = ISBNSearchForm()

    return render(request, "catalog/isbn_search.html",
                  {"form": form, "result": result})