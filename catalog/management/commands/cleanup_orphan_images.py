# catalog/management/commands/cleanup_orphan_images.py
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import BookImage


class Command(BaseCommand):
    help = "Delete orphaned image files in MEDIA_ROOT that are not referenced by any BookImage."

    def handle(self, *args, **options):
        media_root = Path(settings.MEDIA_ROOT)
        image_dir = media_root / "images"

        if not image_dir.exists():
            self.stdout.write(self.style.WARNING(f"No images directory found at {image_dir}"))
            return

        # Build a set of all file paths actually in use by BookImage objects
        db_files = set()
        for image in BookImage.objects.all():
            for field_name in ["image", "thumbnail", "small_thumbnail"]:
                field = getattr(image, field_name)
                if field and field.name:
                    db_files.add(media_root / field.name)

        # Walk through /data/media/images and find files not in db_files
        orphaned_files = []
        for root, _, files in os.walk(image_dir):
            for f in files:
                file_path = Path(root) / f
                if file_path not in db_files:
                    orphaned_files.append(file_path)

        if not orphaned_files:
            self.stdout.write(self.style.SUCCESS("✅ No orphaned image files found."))
            return

        # List and confirm deletion
        self.stdout.write(self.style.WARNING("Found orphaned image files:\n"))
        for f in orphaned_files:
            self.stdout.write(f" - {f}")

        confirm = input("\nDelete these files? (y/N): ").strip().lower()
        if confirm != "y":
            self.stdout.write(self.style.WARNING("Aborted. No files deleted."))
            return

        # Delete files
        for f in orphaned_files:
            try:
                os.remove(f)
                self.stdout.write(self.style.SUCCESS(f"Deleted {f}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error deleting {f}: {e}"))

        self.stdout.write(self.style.SUCCESS("🧹 Cleanup complete."))
