# catalog/services/stats.py
from django.db.models import Avg, Count, Max, Sum
from catalog.models import Author, Bookshelf, Collection, Volume, Work

UNKNOWN_AUTHOR_NAME = "Unknown Author"

def get_library_stats():
    stats = {}
    stats.update(_volume_stats())
    stats.update(_price_stats())
    stats.update(_author_stats())
    stats.update(_bookshelf_stats())
    stats.update(_collection_stats())
    stats.update(_works_stats())
    return stats

def _volume_stats():
    total_volumes = Volume.objects.count()

    return {
        "total_volumes": total_volumes,
    }

def _price_stats():
    priced_volumes = Volume.objects.filter(price__gt=0)
    agg = priced_volumes.aggregate(total=Sum("price"), avg=Avg("price"),
                           max=Max("price"))

    total_volume_cost = agg["total"]
    avg_volume_cost = agg['avg']
    max_volume_cost = agg['max']

    max_cost_volumes = list(priced_volumes.filter(price=max_volume_cost).values(
        "id", "title", "price"))


    return {
        "total_volume_cost": total_volume_cost,
        "avg_volume_cost": avg_volume_cost,
        "max_volume_cost": max_volume_cost,
        "max_cost_volumes": max_cost_volumes,
    }

def _author_stats():
    base = Author.objects.exclude(full_name=UNKNOWN_AUTHOR_NAME)

    total_authors = base.count()

    works_by_author = list(
        base.values("id", "slug", "full_name")
        .annotate(count=Count("works", distinct=True))
        .order_by("-count")
    )

    volumes_by_author = list(
        base.values("id", "slug", "full_name")
        .annotate(count=Count("works__volumes", distinct=True))
        .order_by("-count")
    )

    return {
        "total_authors": total_authors,
        "works_by_author": works_by_author,
        "volumes_by_author": volumes_by_author,
    }


def _bookshelf_stats():
    num_volumes_by_bookshelf = list(Bookshelf.objects.values("pk", "name")
    .annotate(count=Count("volumes"))
    .order_by("-count"))

    return {
        "num_volumes_by_bookshelf": num_volumes_by_bookshelf,
    }

def _collection_stats():

    num_works_by_collection = list(
        Collection.objects.values("name", "slug",)
        .annotate(count=Count("works"))
        .order_by("name")
    )

    return {
        "num_works_by_collection": num_works_by_collection,
    }

def _works_stats():
    total_works = Work.objects.count()

    return {
        "total_works": total_works,
    }

