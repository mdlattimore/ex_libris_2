from django.views.generic import ListView, DetailView, CreateView, UpdateView
from catalog.models import Author


class AuthorCreateView(CreateView):
    model = Author
    context_object_name = "author"
    template_name = "catalog/author_create_update.html"
    fields = "__all__"


class AuthorUpdateView(UpdateView):
    model = Author
    context_object_name = "author"
    template_name = "catalog/author_create_update.html"
    fields = "__all__"


class AuthorListView(ListView):
    model = Author
    context_object_name = 'authors'
    template_name = "catalog/author_list.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        all_authors = Author.objects.all()
        authors_sorted = sorted(all_authors, key=lambda author: author.sort_name)
        context['authors_display'] = authors_sorted
        return context


class AuthorDetailView(DetailView):
    model = Author
    context_object_name = 'author'
    template_name = "catalog/author_detail.html"