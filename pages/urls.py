from django.urls import path

from .views import HomePageView, AboutPageView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("home/", HomePageView.as_view(), name="home"),
    path("about/", AboutPageView.as_view(), name="about"),
]
