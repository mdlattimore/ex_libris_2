# catalog/services/images.py (recommended)
from django.db import transaction
from django.db.models import Max

from ..models import VolumeImage
from ..utils.images.images import process_upload


def ingest_volume_images(*, volume, files, set_first_as_cover: bool = True):
    """
    Creates VolumeImage rows from uploaded files, assigns increasing sort_order,
    and optionally sets volume.cover_image to the first created image.
    """
    if not files:
        return []

    start = (
        VolumeImage.objects.filter(volume=volume).aggregate(m=Max("sort_order")).get("m") or 0
    )

    created = []
    with transaction.atomic():
        for idx, f in enumerate(files, start=1):
            img = VolumeImage(volume=volume, sort_order=start + idx)

            # Reuse your existing processing pipeline
            base, thumb, display, detail = process_upload(f)  # <-- import this

            img.image_thumb.save(f"{base}_thumb.webp", thumb, save=False)
            img.image_display.save(f"{base}_display.webp", display, save=False)
            img.image_detail.save(f"{base}_detail.webp", detail, save=False)

            img.save()
            created.append(img)

        if set_first_as_cover and created:
            volume.cover_image = created[0]
            volume.save(update_fields=["cover_image"])

    return created
