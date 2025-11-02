from django.urls import path
from . import views

urlpatterns = [
    path('author_list/', views.AuthorListView.as_view(), name='author_list'),
    path('author_detail/<int:pk>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('work_list/', views.WorkListView.as_view(), name='work_list'),
    path('work_detail/<int:pk>/', views.WorkDetailView.as_view(), name='work_detail'),
    path('volume_list/', views.VolumeListView.as_view(), name='volume_list'),
    path('volume_detail/<int:pk>/', views.VolumeDetailView.as_view(), name='volume_detail'),
    path('isbn_lookup/', views.isbn_lookup_view, name='isbn_lookup'),
    path('volume_create/', views.volume_create_view, name='volume_create'),
    path("manual-form/", views.manual_volume_form, name="manual_volume_form"),

]