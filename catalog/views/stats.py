from django.db.models import Sum, Avg, Max, Count
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from catalog.models import Volume, Author, Bookshelf, Collection
from catalog.services.stats import get_library_stats

class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_library_stats())
        return context


