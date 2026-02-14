from django.urls import path, include

from .views import ReadingPathDetailView, ReadingPathListView, \
    ReadingPathItemCreateView, ReadingPathCreateView, \
    ReadingPathUpdateView, ReadingPathItemUpdateView, ReadingPathItemDeleteView

urlpatterns = [
    path("reading_path_create/", ReadingPathCreateView.as_view(),
         name="reading_path_create"),
    path("reading_path_update/<int:pk>", ReadingPathUpdateView.as_view(),
         name="reading_path_update"),
    path("reading_path_detail/<int:pk>", ReadingPathDetailView.as_view(),
         name="reading_path_detail"),
    path("reading_path_list/", ReadingPathListView.as_view(),
         name="reading_path_list"),
    # path("reading_path_item_create/", ReadingListItemCreateView.as_view(),
    # name="reading_path_item_create"),
    # reading/urls.py
    path(
        "reading_paths/<int:readingpath_pk>/item/create/",
        ReadingPathItemCreateView.as_view(),
        name="reading_path_item_create",
    ),

    path("reading_path_item_update/<int:pk>",
         ReadingPathItemUpdateView.as_view(), name="reading_path_item_update"),

    path("reading_path_item_delete/<int:pk>",
         ReadingPathItemDeleteView.as_view(), name="reading_path_item_delete"),

    path("markdownx/", include("markdownx.urls")),

]
