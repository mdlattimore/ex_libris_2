from django.db.models import Prefetch

from .base import CatalogBaseView
from catalog.models import Volume, Work, BookSet
from catalog.utils.normalization import normalize_sort_title


# class CatalogAllView(CatalogBaseView):
#     view_type = "all"

from itertools import chain

class CatalogAllView(CatalogBaseView):
    template_name = "catalog/work_list.html"
    view_type = "all"

    def get_queryset(self):
        volumes_qs = Volume.objects.only("id", "title", "cover_url", "slug")

        works = (
            Work.objects
            .select_related("author")
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
        )
        booksets = (
            BookSet.objects
            .prefetch_related(Prefetch("volumes", queryset=volumes_qs))
        )

        return sorted(chain(works, booksets), key=lambda obj: normalize_sort_title(obj.title))
