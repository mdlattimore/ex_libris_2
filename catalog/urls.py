from django.urls import path
from . import views
urlpatterns = [
    path("book_list_all/", views.BookListView.as_view(), name="book_list_all"),
    path('collection/<slug:collection_slug>/', views.BookListView.as_view(),
         name='book_list_collection'),
    path('book_spotlight/<int:pk>/',
         views.BookSpotlightDetailView.as_view(), name='book_spotlight'),
    path("book_add/", views.BookCreateView.as_view(), name="add_book"),
    path("book_search_isbn", views.isbn_search_view, name="isbn_search"),
    path("book_detail/<int:pk>/", views.BookDetailView.as_view(), name="book_detail"),
    path("boxset_detail/<int:pk>/", views.BoxSetDetailView.as_view(),
         name="boxset_detail"),
    path('books/<int:pk>/json/', views.BookJsonView.as_view(),
         name='book_json'),
    path("book_update/<int:pk>/", views.BookUpdateView.as_view(), name="book_update"),
    path("book_delete/<int:pk>/", views.BookDeleteView.as_view(), name="book_delete"),
]