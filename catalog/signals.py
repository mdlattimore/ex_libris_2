from django.db.models.signals import post_delete

from .models import VolumeImage
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from catalog.models import Volume, VolumeWork


@receiver(post_delete, sender=VolumeImage)
def delete_volume_image_files(sender, instance, **kwargs):
    for field_name in ("image_thumb", "image_display", "image_detail"):
        f = getattr(instance, field_name, None)
        if f and f.name:
            f.delete(save=False)




@receiver(m2m_changed, sender=Volume.works.through)
def sync_volumework(sender, instance: Volume, action, reverse, pk_set, **kwargs):
    """
    Keep VolumeWork in sync with the legacy Volume.works M2M.
    Your UI reads from VolumeWork, but your form/admin may still write to Volume.works.
    """
    # instance is a Volume when reverse=False (i.e., volume.works.add(...))
    if reverse:
        # If you ever edit from the Work side (work.volumes.add(...)),
        # you can implement this too, but it's optional.
        return

    if action == "post_add" and pk_set:
        for work_id in pk_set:
            VolumeWork.objects.get_or_create(
                volume_id=instance.id,
                work_id=work_id,
                defaults={"locator": "", "position": 0},
            )

    elif action == "post_remove" and pk_set:
        VolumeWork.objects.filter(volume_id=instance.id, work_id__in=pk_set).delete()

    elif action == "post_clear":
        VolumeWork.objects.filter(volume_id=instance.id).delete()
