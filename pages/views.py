# from django.views.generic import TemplateView
# from catalog.models import BookSpotlight
#
# class HomePageView(TemplateView):
#     template_name = "pages/home.html"
#
#     def get_context_data(self, **kwargs):
#         context = super(HomePageView, self).get_context_data(**kwargs)
#         context['works'] = BookSpotlight.objects.all()
#         return context
#
#
#
# class AboutPageView(TemplateView):
#     template_name = "pages/about.html"

from django.views.generic import TemplateView
from .models import SiteContent


class SiteContentMixin:
    """Provides the single SiteContent instance to templates."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content"] = SiteContent.objects.first()
        return context


class HomePageView(SiteContentMixin, TemplateView):
    template_name = "pages/home.html"

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # Keep your existing spotlight functionality
    #     context["works"] = BookSpotlight.objects.all()
    #     return context


class AboutPageView(SiteContentMixin, TemplateView):
    template_name = "pages/about.html"

