from django.shortcuts import render, redirect
from catalog.book_retrieval import get_book
from catalog.forms import ISBNSearchForm
from pprint import pprint
from catalog.models import Author


def isbn_lookup(request):
    result = None
    if request.method == "POST":
        form = ISBNSearchForm(request.POST)
        if form.is_valid():
            isbn = form.cleaned_data['isbn']
            print("view", isbn)
            try:
                result = get_book(isbn)
                print("View result", result)
            except:
                result = {"none_found": "None found"}
            pprint(result)


    #     if 'save' in request.POST and (
    #             'isbn_10' in request.POST or 'isbn_13' in request.POST):
    #         title = request.POST.get('title')
    #         subtitle = request.POST.get('subtitle')
    #         authors = request.POST.get('author')
    #         additional_contributors = request.POST.get('additional_contributors')
    #         additional_contributors = additional_contributors.lstrip("["
    #                                                                  "").rstrip("]").replace("'", "")
    #         # additional_contributors = "".join(additional_contributors)
    #         publisher = request.POST.get('publisher')
    #         publication_date = request.POST.get('publication_date')
    #         number_of_pages = request.POST.get('number_of_pages')
    #         cover_id = request.POST.get('cover_id')
    #         isbn_10 = request.POST.get('isbn_10')
    #         isbn_13 = request.POST.get('isbn_13')
    #         notes = request.POST.get('notes')
    #         google_info = request.POST.get('google_info')
    #         book_json = request.POST.get('book_json')
    #
    #         # named_author is the [0] index in "authors" from the api response
    #         # we assign it to "named_author" since "authors" can be reassigned
    #         # below
    #
    #         named_author = authors
    #         # check aliases
    #         all_aliases = AuthorAlias.objects.all()
    #         for alias in all_aliases:
    #             # if authors == alias.alias:
    #             if name_match(authors, alias.alias) >= 90:
    #                 authors = alias.author.full_name
    #                 print(f"{alias} for {alias.author}")
    #                 break
    #
    #         all_authors = Author.objects.all()
    #         for author_instance in all_authors:
    #             if name_match(author_instance.full_name, authors) >= 90:
    #                 author = author_instance
    #                 print(name_match(author.full_name, authors))
    #                 break
    #             else:
    #                 author = all_authors.filter(full_name="Unknown Author").first()
    #
    #         # The difference between "author" and "authors" is "authors" is
    #         # from the api response. "author" references the foreign key "author"
    #         # in book model.
    #
    #         # Create or update the book instance
    #         book = Book.objects.create(
    #
    #             title=title,
    #             subtitle=subtitle,
    #             named_author=named_author,
    #             author=author,
    #             additional_contributors=additional_contributors,
    #             publisher=publisher,
    #             publication_date=publication_date,
    #             number_of_pages=number_of_pages,
    #             cover_id=cover_id,
    #             isbn_10=isbn_10,
    #             isbn_13=isbn_13,
    #             notes=notes,
    #             google_info=google_info,
    #             book_json=book_json,
    #         )
    #         return redirect("book_detail", pk=book.id)
    #
    # else:
    #     form = ISBNSearchForm

    return render(request, "catalog/isbn_search.html",
                  {"form": form, "result": result})