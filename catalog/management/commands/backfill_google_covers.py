import time
from django.core.management.base import BaseCommand

from catalog.models import Volume
from catalog.services.covers_google import cache_google_cover_for_volume


class Command(BaseCommand):
    help = "Backfill cached cover images from Volume.cover_url (Google) into VolumeImage and set Volume.cover_image."

    def add_arguments(self, parser):
        parser.add_argument("--sleep", type=float, default=1.0, help="Seconds to sleep between downloads.")
        parser.add_argument("--limit", type=int, default=0, help="Max volumes to process (0 = no limit).")
        parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without downloading.")
        parser.add_argument("--only-missing-cover-url", action="store_true",
                            help="(Debug) Show volumes missing cover_url as well.")

    def handle(self, *args, **opts):
        sleep = opts["sleep"]
        limit = opts["limit"]
        dry_run = opts["dry_run"]
        show_missing = opts["only_missing_cover_url"]

        qs = Volume.objects.filter(cover_image__isnull=True)

        if show_missing:
            missing = qs.filter(cover_url__isnull=True) | qs.filter(cover_url__exact="")
            self.stdout.write(self.style.WARNING(f"Missing cover_url: {missing.count()} volumes"))
            return

        qs = qs.exclude(cover_url__isnull=True).exclude(cover_url__exact="")

        total = qs.count() if not limit else min(qs.count(), limit)
        self.stdout.write(f"Will process up to {total} volumes (sleep={sleep}s, dry_run={dry_run})")

        if limit:
            qs = qs[:limit]

        ok = 0
        skipped = 0

        for v in qs.iterator():
            if dry_run:
                self.stdout.write(f"[DRY RUN] {v.pk} | {v.title}")
                continue

            if cache_google_cover_for_volume(v):
                ok += 1
                self.stdout.write(self.style.SUCCESS(f"Cached {v.pk} | {v.title}"))
            else:
                skipped += 1
                self.stdout.write(self.style.WARNING(f"Skipped {v.pk} | {v.title}"))

            time.sleep(sleep)

        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run complete (no downloads performed)."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. Cached={ok}, Skipped/Failed={skipped}"))
