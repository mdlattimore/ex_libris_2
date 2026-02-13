from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model # type: ignore
from catalog.models import Volume
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.conf import settings
user = get_user_model()


class ReadingList(models.Model):
    name = models.CharField(max_length=200)
    theme = models.CharField(max_length=200)
    description = MarkdownxField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_lists",
    )

    class Meta:
        ordering = ("name",)

    class Meta:
        ordering = ["name"]

    @property
    def description_html(self):
        return markdownify(self.description or "")

    def __str__(self):
        return self.name


class ReadingListItem(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        READING = "READING", "Reading"
        COMPLETE = "COMPLETE", "Complete"


    reading_list = models.ForeignKey(ReadingList, on_delete=models.CASCADE, related_name="items")
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE,
                               related_name="reading_list_items")
    position = models.PositiveIntegerField(default=0)
    notes = MarkdownxField(blank=True, default="")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ("position", "created_at")
        constraints = UniqueConstraint(
            fields=("reading_list", "volume"),
            name = "uniq_readinglistitem_list_volume"
        ),
        UniqueConstraint(
            fields=("reading_list", "position"),
            name = "uniq_readinglistitem_list_position",
        )

    @property
    def notes_html(self):
        return markdownify(self.notes or "")

    def __str__(self):
        return f"{self.reading_list.name} - {self.volume.title}"
