from django.contrib.auth.models import User
from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import get_user_model # type: ignore
from catalog.models import Volume, Work
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.conf import settings
from django.urls import reverse

user = get_user_model()


# class ReadingPath(models.Model):
#     name = models.CharField(max_length=200)
#     theme = models.CharField(max_length=200, blank=True, default="")
#     description = MarkdownxField(blank=True, default="")
#     overview_notes = MarkdownxField(blank=True, default="")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     owner = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="reading_paths",
#     )
#
#
#
#     def get_absolute_url(self):
#         return reverse("reading_path_detail", args=[self.pk])
#
#     class Meta:
#         ordering = ("name",)
#
#
#
#     @property
#     def description_html(self):
#         return markdownify(self.description or "")
#
#     @property
#     def overview_notes_html(self):
#         return markdownify(self.overview or "")
#
#     def __str__(self):
#         return self.name
#
#
# class ReadingPathItem(models.Model):
#     class Status(models.TextChoices):
#         PLANNED = "PLANNED", "Planned"
#         READING = "READING", "Reading"
#         COMPLETE = "COMPLETE", "Complete"
#
#
#     reading_path = models.ForeignKey(ReadingPath, on_delete=models.CASCADE,
#                                      related_name="items")
#     volume = models.ForeignKey(Volume, on_delete=models.CASCADE,
#                                related_name="reading_path_items")
#     position = models.PositiveIntegerField(default=0)
#     notes = MarkdownxField(blank=True, default="")
#     status = models.CharField(
#         max_length=10,
#         choices=Status.choices,
#         default=Status.PLANNED,
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def get_absolute_url(self):
#         return reverse("reading_path_detail", args=[self.reading_path.pk])
#
#     class Meta:
#         ordering = ("position", "created_at")
#         constraints = UniqueConstraint(
#             fields=("reading_path", "volume"),
#             name = "uniq_readingpathitem_list_volume"
#         ),
#         UniqueConstraint(
#             fields=("reading_path", "position"),
#             name = "uniq_readingpathitem_list_position",
#         )
#
#     @property
#     def notes_html(self):
#         return markdownify(self.notes or "")
#
#     def __str__(self):
#         return f"{self.reading_path.name} - {self.volume.title}"

class ReadingPath(models.Model):
    name = models.CharField(max_length=200)
    description = MarkdownxField(blank=True, default="")
    overview_notes = MarkdownxField(blank=True, default="")  # rename from global_notes
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reading_paths",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse("reading_path_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.name


class ReadingPathItem(models.Model):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        READING = "READING", "Reading"
        COMPLETE = "COMPLETE", "Complete"

    reading_path = models.ForeignKey(
        ReadingPath,
        on_delete=models.CASCADE,
        related_name="items",
    )

    # the *thing* you intend to read/study
    work = models.ForeignKey(
        Work,
        on_delete=models.PROTECT,
        related_name="reading_path_items",

    )

    # optional: the edition/container you’re using
    source_volume = models.ForeignKey(
        Volume,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reading_path_source_items",
    )

    position = models.PositiveIntegerField(default=0)
    notes = MarkdownxField(blank=True, default="")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PLANNED)

    # optional but extremely useful for essays/chapters
    locator = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text='e.g., "Essay in The Monsters and the Critics", "pp. 109–161", "Ch. 3"',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def notes_html(self):
        return markdownify(self.notes)

    class Meta:
        ordering = ("position", "created_at")
        constraints = [
            models.UniqueConstraint(
                fields=("reading_path", "work"),
                name="uniq_readingpathitem_path_work",
            ),
            models.UniqueConstraint(
                fields=("reading_path", "position"),
                name="uniq_readingpathitem_path_position",
            ),
        ]


    def __str__(self):
        return f"{self.reading_path.name} — {self.work}"