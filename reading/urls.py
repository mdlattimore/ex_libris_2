from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import ReadingListDetailView

urlpatterns = [
    path("reading_list_detail/<int:pk>", ReadingListDetailView.as_view(),
    name="reading_list_detail")
]