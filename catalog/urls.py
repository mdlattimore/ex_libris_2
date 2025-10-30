from django.urls import path
from . import views
urlpatterns = [
    path('work_list/', views.WorkListView.as_view(), name='work_list'),
    path('work_detail/<int:pk>/', views.WorkDetailView.as_view(), name='work_detail'),
    path('volume_detail/<int:pk>/', views.VolumeDetailView.as_view(), name='volume_detail'),
]