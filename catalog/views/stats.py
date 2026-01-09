from django.db.models import Sum, Avg, Max, Count
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from catalog.models import Volume, Author, Collection


class StatsView(LoginRequiredMixin, TemplateView):
    template_name = "catalog/stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_volumes"] = Volume.objects.count()
        context["total_cost"] = (
            Volume.objects.filter(price__gt=0)
            .aggregate(Sum("price"))
            ["price__sum"]
        )
        context["avg_cost"] = (
            Volume.objects.filter(price__gt=0)
            .aggregate(Avg("price"))
            ["price__avg"]
        )
        context["max_cost"] = Volume.objects.aggregate(Max("price"))[
            "price__max"]
        context["max_cost_volume"] = Volume.objects.filter(
            price=Volume.objects.aggregate(Max("price"))["price__max"])
        # subtract 1 from total_authors to account for Unknown Author row
        context["total_authors"] = Author.objects.count() - 1
        context["authors_by_nationality"] = (
            Author.objects.values("nationality")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        context["num_volumes_by_collection"] = (
            Collection.objects.values("name")
            .annotate(count=Count("volumes"))
            .order_by("name")
        )
        return context
