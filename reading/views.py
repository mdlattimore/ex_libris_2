from django.shortcuts import render
from django.views.generic import DetailView

from reading.models import ReadingList


class ReadingListDetailView(DetailView):
    model = ReadingList
    context_object_name = 'readinglist'
    template_name = "reading/reading_list_detail.html"