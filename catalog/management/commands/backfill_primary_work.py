from django.core.management.base import BaseCommand
from django.db import transaction
from catalog.models import Volume


class Command(BaseCommand):
    help = "Backfill Volume.primary_work with first related Work (by ID)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without saving changes",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        volumes = (
            Volume.objects
            .filter(primary_work__isnull=True)
            .prefetch_related("works")
        )

        updated = 0
        skipped = 0

        for volume in volumes:
            works = list(volume.works.all())

            if not works:
                skipped += 1
                continue

            first_work = sorted(works, key=lambda w: w.pk)[0]

            if dry_run:
                self.stdout.write(
                    f"[DRY RUN] Would set Volume {volume.pk} -> Work {first_work.pk}"
                )
            else:
                volume.primary_work = first_work
                volume.save(update_fields=["primary_work"])

            updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Updated: {updated}, Skipped (no works): {skipped}"
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING("No changes saved (dry run)."))
