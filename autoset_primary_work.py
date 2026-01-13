from catalog.models import Volume

updated = 0

for v in Volume.objects.filter(primary_work__isnull=True):
    works = v.works.all()
    if works.count() == 1:
        v.primary_work = works[0]
        v.save(update_fields=["primary_work"])
        updated += 1

print(f"Auto-set primary_work on {updated} volumes.")
