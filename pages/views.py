from django.views.generic import TemplateView
from library.models import BookSpotlight

class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['works'] = BookSpotlight.objects.all()
        return context



class AboutPageView(TemplateView):
    template_name = "pages/about.html"
