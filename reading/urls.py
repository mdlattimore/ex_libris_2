from django.urls import path, include

from .views import ReadingListDetailView, ReadingListListView, \
    ReadingListItemCreateView, ReadingListItemUpdateView, ReadingListCreateView, \
    ReadingListUpdateView

urlpatterns = [
    path("reading_list_create/", ReadingListCreateView.as_view(),
         name="reading_list_create"),
    path("reading_list_update/<int:pk>", ReadingListUpdateView.as_view(),
         name="reading_list_update"),
    path("reading_list_detail/<int:pk>", ReadingListDetailView.as_view(),
         name="reading_list_detail"),
    path("reading_list_list/", ReadingListListView.as_view(),
         name="reading_list_list"),
    # path("reading_list_item_create/", ReadingListItemCreateView.as_view(),
    # name="reading_list_item_create"),
    # reading/urls.py
    path(
        "reading_lists/<int:readinglist_pk>/item/create/",
        ReadingListItemCreateView.as_view(),
        name="reading_list_item_create",
    ),

    path("reading_list_item_update/<int:pk>",
         ReadingListItemUpdateView.as_view(), name="reading_list_item_update"),

    path("markdownx/", include("markdownx.urls")),

]
