from django.urls import path

from . import views
from .views import work_redirect_by_id
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('author_create/', views.AuthorCreateView.as_view(),
         name='author_create'),
    path('author_create_modal/', views.AuthorCreateModalView.as_view(),
         name='author_create_modal'),
    path('author_update/<int:pk>/', views.AuthorUpdateView.as_view(),
         name='author_update'),
    path('author_list/', views.AuthorListView.as_view(), name='author_list'),
    path('author_detail/<int:pk>/', views.author_redirect_by_id,
         name="author_detail_old"),
    path('author_detail/<slug:slug>/', views.AuthorDetailView.as_view(),
         name='author_detail'),

    path('work_create/', views.WorkCreateView.as_view(), name='work_create'),
    path('work_create_modal/', views.WorkCreateModalView.as_view(),
         name='work_create_modal'),
    path('work_update/<int:pk>/', views.WorkUpdateView.as_view(),
         name='work_update'),
    path('work_list/', views.WorkListView.as_view(), name='work_list'),
    path('work_detail/<int:pk>/', views.work_redirect_by_id,
         name='work_detail_old'),
    path('work_detail/<slug:slug>/', views.WorkDetailView.as_view(),
         name='work_detail'),

    path('volume_list/', views.VolumeListView.as_view(), name='volume_list'),
    # OLD URL — keep it above the slug pattern
    path("volume_detail/<int:pk>/", views.volume_redirect_by_id,
         name="volume_detail_old"),
    path('volume_detail/<slug:slug>/', views.VolumeDetailView.as_view(),
         name='volume_detail'),
    path('volume_update/<int:pk>/', views.VolumeUpdateView.as_view(),
         name='volume_update'),
    path( "volume_detail/<slug:slug>/images/add/",
          views.VolumeImageUploadView.as_view(), name="volume_image_add"),

    path('bookset_list/', views.BookSetListView.as_view(), name='bookset_list'),
    path('bookset_detail/<int:pk>/', views.bookset_redirect_by_id,
         name='bookset_detail_old'),
    path('bookset_detail/<slug:slug>/', views.BookSetDetailView.as_view(),
         name='bookset_detail'),

    path('catalog/', views.CatalogAllView.as_view(), name='catalog_all'),
    path('isbn_lookup/', views.isbn_lookup_view, name='isbn_lookup'),
    path('volume_create/', views.volume_create_view, name='volume_create'),
    path('collection_create/', views.CollectionCreateView.as_view(),
         name='collection_create'),
    path('collection_update/<int:pk>/', views.CollectionUpdateView.as_view(),
         name='collection_update'),
    path('collection_list/', views.CollectionListView.as_view(),
         name='collection_list'),

    path('collection_detail/<int:pk>/', work_redirect_by_id,
         name='collection_detail_old'),
    path('collection_detail/<slug:slug>/',
         views.CollectionDetailView.as_view(), name='collection_detail'),

    path("manual-form/", views.manual_volume_form, name="manual_volume_form"),
    path("search/", views.SearchResultsView.as_view(), name="search_results"),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('pricing_calculator/', views.pricing_view, name='pricing_calculator'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
