from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView, CreateView, UpdateView

from reading.models import ReadingList, ReadingListItem


class ReadingListCreateView(CreateView):
    model = ReadingList
    context_object_name = 'readinglist'
    template_name = "reading/reading_list_create_update.html"
    fields = ["name", "theme", "description", "overview_notes"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ReadingListUpdateView(UpdateView):
    model = ReadingList
    context_object_name = 'readinglist'
    template_name = "reading/reading_list_create_update.html"
    fields = "__all__"

class ReadingListDetailView(DetailView):
    model = ReadingList
    context_object_name = 'readinglist'
    template_name = "reading/reading_list_detail.html"




class ReadingListListView(ListView):
    model = ReadingList
    context_object_name = 'readinglists'
    template_name = "reading/reading_list_list.html"


# class ReadingListItemCreateView(CreateView):
#     model = ReadingListItem
#     context_object_name = 'item'
#     template_name = "reading/reading_list_item_create_update.html"
#     fields = ["volume", "position", "notes", "status"]

class ReadingListItemCreateView(LoginRequiredMixin, CreateView):
    model = ReadingListItem
    context_object_name = "item"
    template_name = "reading/reading_list_item_create_update.html"
    fields = ["volume", "position", "notes", "status"]

    def dispatch(self, request, *args, **kwargs):
        self.reading_list = get_object_or_404(
            ReadingList,
            pk=kwargs["readinglist_pk"],
            owner=request.user,   # important: prevents guessing other users' PKs
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.reading_list = self.reading_list
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["readinglist"] = self.reading_list
        return ctx

    def get_success_url(self):
        return self.reading_list.get_absolute_url()


# class ReadingListItemUpdateView(UpdateView):
#     model = ReadingListItem
#     context_object_name = 'item'
#     template_name = "reading/reading_list_item_create_update.html"
#     fields = ["volume", "position", "notes", "status"]
class ReadingListItemUpdateView(UpdateView):
    model = ReadingListItem
    context_object_name = 'item'
    template_name = "reading/reading_list_item_create_update.html"
    fields = ["volume", "position", "notes", "status"]

    def get_queryset(self):
        # security: only allow editing items on the current user's lists
        return ReadingListItem.objects.filter(
            reading_list__owner=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["readinglist"] = self.object.reading_list
        return context

    def get_success_url(self):
        return self.object.reading_list.get_absolute_url()
