from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import VolumeImage

@receiver(post_delete, sender=VolumeImage)
def delete_volume_image_files(sender, instance, **kwargs):
    for field_name in ("image_thumb", "image_display", "image_detail"):
        f = getattr(instance, field_name, None)
        if f and f.name:
            f.delete(save=False)
