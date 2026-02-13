# NOT CURRENTLY USED #
# DELETABLE #

from django.views.generic import TemplateView

from catalog.models import Work, BookSet
from django.views.generic import ListView
from catalog.utils.normalization import normalize_sort_title


class CatalogBaseView(ListView):
    template_name = ...
    context_object_name = "items"
    paginate_by = 20

    # view_type = "all"  # default

    # def get_queryset(self):
    #     # sensible default; subclasses can override
    #     from itertools import chain
    #     items = list(Work.objects.all()) + list(BookSet.objects.all())
    #     return sorted(items, key=lambda i: normalize_sort_title(i.title))
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     view_type = getattr(self, "view_type", "all")
    #
    #     if view_type == "works":
    #         context["heading"] = "Works"
    #         context["sub_heading"] = (
    #             "Creative texts (novels, poems, essays, or stories) independent of any "
    #             "particular edition or printing."
    #         )
    #     elif view_type == "booksets":
    #         context["heading"] = "Book Sets"
    #         context["sub_heading"] = (
    #             "A group of volumes published or packaged as a unit. May or may not be 'boxed.'"
    #         )
    #     else:
    #         context["heading"] = "All Works and Book Sets"
    #         context["sub_heading"] = ""
    #
    #     context["view_type"] = view_type
    #     return context
