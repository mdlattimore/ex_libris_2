from django.views.generic import ListView, DetailView
from itertools import chain
from .models import Work, Volume, BookSet, Author
from django.db.models.functions import Lower



class AuthorListView(ListView):
    model = Author
    context_object_name = 'authors'
    template_name = "catalog/author_list.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        all_authors = Author.objects.all()
        authors_sorted = sorted(all_authors, key=lambda author: author.last_name
                                                                + " " +
                                                                author.first_name)
        context['authors_display'] = authors_sorted
        return context


class AuthorDetailView(DetailView):
    model = Author
    context_object_name = 'author'
    template_name = "catalog/author_detail.html"



class WorkListView(ListView):
    model = Work
    context_object_name = "items"
    template_name = "catalog/work_list.html"

    def get_queryset(self):
        """
        Combine Work and BookSet objects into one unified queryset,
        sorted alphabetically by title.
        """
        works = Work.objects.all().prefetch_related("volumes")
        booksets = BookSet.objects.all().prefetch_related("volumes")

        # Combine and sort
        combined = chain(works, booksets)
        sorted_combined = sorted(combined, key=lambda obj: obj.title.lower())

        return sorted_combined

    def get_context_data(self, **kwargs):
        """
        Override to ensure the template context variable name matches expectations.
        """
        context = super().get_context_data(**kwargs)
        context["works"] = self.get_queryset()
        return context


class WorkDetailView(DetailView):
    model = Work
    context_object_name = "work"
    template_name = "catalog/work_detail.html"


class VolumeListView(ListView):
    model = Volume
    context_object_name = 'volumes'
    template_name = "catalog/volume_list.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["volumes_display"] = Volume.objects.order_by(Lower("title"))
    #     return context
    def get_queryset(self):
        # Include related BoxSet to avoid extra queries
        qs = (
            Volume.objects.select_related("book_set")
            .order_by(
                Lower("book_set__title"),  # sort by set name (nulls first)
                Lower("title"),  # then by volume title
            )
        )
        return qs


class VolumeDetailView(DetailView):
    model = Volume
    context_object_name = "volume"
    template_name = "catalog/volume_detail.html"