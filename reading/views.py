from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView, \
    DeleteView

from reading.models import ReadingPath, ReadingPathItem


class ReadingPathCreateView(CreateView):
    model = ReadingPath
    context_object_name = 'readingpath'
    template_name = "reading/reading_path_create_update.html"
    fields = ["name", "description", "overview_notes"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ReadingPathUpdateView(UpdateView):
    model = ReadingPath
    context_object_name = 'readingpath'
    template_name = "reading/reading_path_create_update.html"
    fields = "__all__"

class ReadingPathDetailView(DetailView):
    model = ReadingPath
    context_object_name = 'readingpath'
    template_name = "reading/reading_path_detail.html"




class ReadingPathListView(ListView):
    model = ReadingPath
    context_object_name = 'readingpaths'
    template_name = "reading/reading_path_list.html"


# class ReadingListItemCreateView(CreateView):
#     model = ReadingListItem
#     context_object_name = 'item'
#     template_name = "reading/reading_path_item_create_update.html"
#     fields = ["volume", "position", "notes", "status"]

class ReadingPathItemCreateView(LoginRequiredMixin, CreateView):
    model = ReadingPathItem
    context_object_name = "item"
    template_name = "reading/reading_path_item_create_update.html"
    fields = ["work", "source_volume", "locator", "position", "notes", "status"]

    def dispatch(self, request, *args, **kwargs):
        self.reading_path = get_object_or_404(
            ReadingPath,
            pk=kwargs["readingpath_pk"],
            owner=request.user,   # important: prevents guessing other users' PKs
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.reading_path = self.reading_path
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["readingpath"] = self.reading_path
        return ctx

    def get_success_url(self):
        return self.reading_path.get_absolute_url()


# class ReadingListItemUpdateView(UpdateView):
#     model = ReadingListItem
#     context_object_name = 'item'
#     template_name = "reading/reading_path_item_create_update.html"
#     fields = ["volume", "position", "notes", "status"]
class ReadingPathItemUpdateView(UpdateView):
    model = ReadingPathItem
    context_object_name = 'item'
    template_name = "reading/reading_path_item_create_update.html"
    fields = ["work", "source_volume", "locator", "position", "notes", "status"]

    def get_queryset(self):
        # security: only allow editing items on the current user's lists
        return ReadingPathItem.objects.filter(
            reading_path__owner=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["readingpath"] = self.object.reading_path
        return context

    def get_success_url(self):
        return self.object.reading_path.get_absolute_url()

class ReadingPathItemDeleteView(DeleteView):
    model = ReadingPathItem

    def get_success_url(self):
        return self.object.reading_path.get_absolute_url()