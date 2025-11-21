from django.urls import path
from . import views

urlpatterns = [
    path('author_list/', views.AuthorListView.as_view(), name='author_list'),
    path('author_detail/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('work_list/', views.WorkListView.as_view(), name='work_list'),
    path('work_detail/<int:pk>/', views.WorkDetailView.as_view(), name='work_detail'),
    path('volume_list/', views.VolumeListView.as_view(), name='volume_list'),
    path('volume_detail/<int:pk>/', views.VolumeDetailView.as_view(), name='volume_detail'),
    path('bookset_list/', views.BookSetListView.as_view(), name='bookset_list'),
    path('bookset_detail/<int:pk>/', views.BookSetDetailView.as_view(), name='bookset_detail'),
    path('catalog/', views.CatalogAllView.as_view(), name='catalog_all'),
    path('isbn_lookup/', views.isbn_lookup_view, name='isbn_lookup'),
    path('volume_create/', views.volume_create_view, name='volume_create'),
    path('collection_list/', views.CollectionListView.as_view(), name='collection_list'),
    path('collection_detail/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path("manual-form/", views.manual_volume_form, name="manual_volume_form"),
    path("search/", views.SearchResultsView.as_view(), name="search_results"),
    path('stats/', views.StatsView.as_view(), name='stats'),

]