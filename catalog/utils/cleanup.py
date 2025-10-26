# catalog/utils/cleanup.py
import os
from pathlib import Path
from django.conf import settings
from catalog.models import BookImage


def find_orphan_images():
    """Return a list of Paths for image files not linked to any BookImage."""
    media_root = Path(settings.MEDIA_ROOT)
    image_dir = media_root / "images"

    if not image_dir.exists():
        return []

    db_files = set()
    for image in BookImage.objects.all():
        for field_name in ["image", "thumbnail", "small_thumbnail"]:
            field = getattr(image, field_name)
            if field and field.name:
                db_files.add(media_root / field.name)

    orphaned_files = []
    for root, _, files in os.walk(image_dir):
        for f in files:
            file_path = Path(root) / f
            if file_path not in db_files:
                orphaned_files.append(file_path)

    return orphaned_files


def delete_orphan_images(orphaned_files):
    """Delete the given list of image files."""
    for f in orphaned_files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Error deleting {f}: {e}")
