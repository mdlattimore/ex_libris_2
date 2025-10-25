from django.shortcuts import render

from .fuzzy_name_match_util import name_match, match_parse_name
from .models import Book, Collection, BookSpotlight, BoxSet, Author, AuthorAlias
from .forms import BookForm, ISBNSearchForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (CreateView, ListView, DetailView,
                                  UpdateView, DeleteView)
from django.contrib import messages
from django.urls import reverse_lazy
from .book_retrieval import get_book
from pprint import pprint
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import json
import ast
from django.contrib.auth.mixins import LoginRequiredMixin
import markdown



@method_decorator(never_cache, name='dispatch')
class BookListView(ListView):
    model = Book
    template_name = "books/book_list.html"
    ordering = ['sort_title']
    context_object_name = "books"

    def get_queryset(self):
        slug = self.kwargs.get('collection_slug')
        if slug:
            self.collection = get_object_or_404(Collection, slug__iexact=slug)
            return Book.objects.filter(collection=self.collection).order_by('sort_title')
        else:
            self.collection = None
            return Book.objects.all().order_by('sort_title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collection'] = self.collection
        return context


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_input.html'

    # success_url = reverse_lazy('book_list')  # Replace 'book_list' with the name of your list view URL

    def form_valid(self, form):
        messages.success(self.request, "Book added successfully!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})


class BookSpotlightDetailView(DetailView):
    model = BookSpotlight
    template_name = "books/book_spotlight.html"
    context_object_name = "book_spotlight"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editions'] = self.object.editions.all().order_by('sort_title')
        return context






def isbn_search_view(request):
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


        if 'save' in request.POST and (
                'isbn_10' in request.POST or 'isbn_13' in request.POST):
            title = request.POST.get('title')
            subtitle = request.POST.get('subtitle')
            authors = request.POST.get('author')

            publisher = request.POST.get('publisher')
            publication_date = request.POST.get('publication_date')
            number_of_pages = request.POST.get('number_of_pages')
            cover_id = request.POST.get('cover_id')
            isbn_10 = request.POST.get('isbn_10')
            isbn_13 = request.POST.get('isbn_13')
            notes = request.POST.get('notes')
            google_info = request.POST.get('google_info')
            book_json = request.POST.get('book_json')

            # named_author is the [0] index in "authors" from the api response
            # we assign it to "named_author" since "authors" can be reassigned
            # below
            named_author = authors
            # check aliases
            all_aliases = AuthorAlias.objects.all()
            for alias in all_aliases:
                # if authors == alias.alias:
                if name_match(authors, alias.alias) >= 90:
                    authors = alias.author.full_name
                    print(f"{alias} for {alias.author}")
                    break

            all_authors = Author.objects.all()
            for author_instance in all_authors:
                if name_match(author_instance.full_name, authors) >= 90:
                    author = author_instance
                    print(name_match(author.full_name, authors))
                    break
                else:
                    author = None

            # The difference between "author" and "authors" is "authors" is
            # from the api response. "author" references the foreign key "author"
            # in book model.

            # Create or update the book instance
            book = Book.objects.create(

                title=title,
                subtitle=subtitle,
                named_author=named_author,
                author=author,
                publisher=publisher,
                publication_date=publication_date,
                number_of_pages=number_of_pages,
                cover_id=cover_id,
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                notes=notes,
                google_info=google_info,
                book_json=book_json,
            )
            return redirect("book_detail", pk=book.id)

    else:
        form = ISBNSearchForm

    return render(request, "books/isbn_search.html",
                  {"form": form, "result": result})


@method_decorator(never_cache, name='dispatch')
class BookDetailView(DetailView):
    model = Book
    template_name = "books/book_detail.html"

@method_decorator(never_cache, name='dispatch')
class AuthorDetailView(DetailView):
    model = Author
    template_name = "books/author_detail.html"


@method_decorator(never_cache, name='dispatch')
class BoxSetDetailView(DetailView):
    model = BoxSet
    template_name = "books/boxset_detail.html"



class BookJsonView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'partials/book_json_partial.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        raw_data = self.object.book_json

        try:
            # Safely parse string to Python object
            python_obj = ast.literal_eval(raw_data)
            # Convert back to a JSON-formatted string
            pretty_json = json.dumps(python_obj, indent=4)
        except (ValueError, SyntaxError):
            pretty_json = "Invalid JSON-like string"

        context['pretty_json'] = pretty_json
        return context


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = "books/book_input.html"
    # fields = ['title', 'author', 'publisher', 'publication_date',
    #     'number_of_pages', 'isbn_10', 'isbn_13', 'price',
    #     'date_acquired', 'notes', 'cover_id']

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        if not self.request.user.is_superuser:
            if 'book_json' in form.fields:
                del form.fields['book_json']

        return form

class BookDeleteView(DeleteView):
    model = Book
    template_name = "books/book_confirm_delete.html"
    success_url = reverse_lazy('book_list_all')