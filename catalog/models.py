import os
from io import BytesIO

from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.html import mark_safe
from django.utils.text import slugify
from simple_name_parser import NameParser

from .fuzzy_name_match_util import match_parse_name

parser = NameParser()
parse_name = parser.parse_name


class Author(models.Model):
    full_name = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    dod = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    sort_name = models.CharField(max_length=150, blank=True, null=True)
    match_name = models.CharField(max_length=150, blank=True, null=True,
                                  unique=True)

    @property
    def author_image(self):
        return self.author_images.filter().first()

    def save(self, *args, **kwargs):
        # Parse full_name into first and last names before saving.
        # The function used (parse_name()) returns a named tuple
        name_parts = parse_name(self.full_name)
        self.first_name = name_parts.given_name
        self.middle_name = name_parts.middle_name
        self.last_name = name_parts.surname
        full_sort_name = []
        full_sort_name.append(name_parts.surname)
        full_sort_name.append(name_parts.given_name)
        full_sort_name = " ".join(full_sort_name)
        if "of" in self.full_name.split() or "Of" in self.full_name.split():
            self.sort_name = self.full_name
        else:
            self.sort_name = full_sort_name
        self.match_name = match_parse_name(self.full_name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

class AuthorAlias(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='aliases')
    alias = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "aliases"

    def __str__(self):
        return f"{self.alias} = {self.author.full_name}"



class BookSpotlight(models.Model):
    class Meta:
        verbose_name_plural = "Book Spotlights"

    title = models.CharField(max_length=200)
    # slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    # author = models.ForeignKey("Author", on_delete=models.SET_NULL(),
    #                            null=True, blank=True)
    author = models.CharField(max_length=150, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class Book(models.Model):
    BINDING_CHOICES = [
        ("HC", "Hardcover"),
        ("PB", "Paperback"),
        ("LI", "Library Binding"),
        ("EB", "Ebook"),
        ("OT", "Other"),
    ]
    CONDITION_CHOICES = [
        ("AN", "As New"),
        ("FI", "Fine"),
        ("NF", "Near Fine"),
        ("VG", "Very Good"),
        ("GO", "Good"),
        ("FA", "Fair"),
        ("RC", "Reading Copy")
    ]
    STATUS_CHOICES = [
        ("Catalog", "Catalog"),
        ("Inventory", "Inventory"),
    ]
    DISPOSITION_CHOICES = [
        ("Sold", "Sold"),
        ("Donated", "Donated"),
        ("Gifted", "Gifted"),
        ("Discarded", "Discarded"),

    ]

    # bibliographic info
    collection = models.ForeignKey("Collection", on_delete=models.CASCADE,
                                   related_name="books", blank=True, null=True)
    book_spotlight = models.ForeignKey(BookSpotlight,
                                       on_delete=models.SET_NULL, blank=True,
                                       null=True, related_name="editions")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True, null=True)
    named_author = models.CharField(max_length=150, blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, blank=True,
                               null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_date = models.CharField(max_length=50, blank=True, null=True)
    number_of_pages = models.CharField(max_length=10, blank=True, null=True)
    isbn_10 = models.CharField(max_length=15, blank=True, null=True)
    isbn_13 = models.CharField(max_length=20, blank=True, null=True)
    genres = models.ManyToManyField("Genre", related_name="book_genres",
                                    blank=True)
    cover_id = models.CharField(max_length=250, blank=True, null=True)

    # collection data
    # owned = models.BooleanField(default=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Catalog")
    date_acquired = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True,
                                null=True)
    acquisition_cost = models.DecimalField(decimal_places=2, max_digits=10,
                                           blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    boxset = models.ForeignKey("BoxSet", on_delete=models.SET_NULL, blank=True,
                               null=True, related_name="books")

    # condition and collectibility
    binding = models.CharField(max_length=30, choices=BINDING_CHOICES,
                               blank=True, null=True)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES,
                                 blank=True, null=True)
    dust_jacket = models.BooleanField(default=False)
    dust_jacket_condition = models.CharField(max_length=30,
                                             choices=CONDITION_CHOICES,
                                             blank=True, null=True)
    signed_by_author = models.BooleanField(default=False)
    collectibility_notes = models.TextField(blank=True, null=True)
    est_value = models.DecimalField(decimal_places=2, max_digits=10, blank=True,
                                    null=True)

    # Disposition
    disposition = models.CharField(max_length=30,
                                   choices=DISPOSITION_CHOICES, blank=True,
                                   null=True)
    recipient = models.CharField(max_length=150, blank=True, null=True)
    sales_price = models.DecimalField(decimal_places=2, blank=True,
                                      null=True, max_digits=10)
    shipping_charged = models.DecimalField(decimal_places=2, max_digits=10,
                                           blank=True, null=True)
    shipping_cost = models.DecimalField(decimal_places=2, blank=True,
                                        null=True, max_digits=10)
    disposition_date = models.DateField(blank=True, null=True)

    # utility
    # sort_name = models.CharField(max_length=150, editable=True)
    sort_title = models.CharField(max_length=150, editable=True)
    google_info = models.CharField(max_length=200, blank=True, null=True)
    gutenburg_info = models.CharField(max_length=200, blank=True, null=True)
    book_json = models.TextField(blank=True, null=True)

    @property
    def cover_image(self):
        return self.images.filter(is_cover=True).first()

    @property
    def total_cost(self):
        if self.price and self.acquisition_cost:
            return self.price + self.acquisition_cost
        elif self.price:
            return self.price
        else:
            return ""

    @property
    def total_sold_price(self):
        if self.sales_price and self.shipping_charged:
            return self.sales_price + self.shipping_charged
        elif self.sales_price:
            return self.sales_price
        else:
            return ""

    @property
    def total_profit(self):
        if self.total_cost and self.total_sold_price:
            return (self.sales_price - self.price) + (self.shipping_charged -
                                                      self.acquisition_cost
                                                      - self.shipping_cost
                                                      )
        else:
            return ""

    def normalize_sort_title(self, title):
        articles = ["a ", "an ", "the "]
        lower_title = title.lower()
        for article in articles:
            if lower_title.startswith(article):
                return title[len(article):].strip()
        return title.strip()

    def save(self, *args, **kwargs):
        # Parse full_name into first and last names before saving.
        # The function used (parse_name()) returns a named tuple
        # name_parts = parse_name(self.author.full_name)
        # full_sort_name = []
        # full_sort_name.append(name_parts.surname)
        # full_sort_name.append(name_parts.given_name)
        # full_sort_name.append(self.title)
        # full_sort_name = " ".join(full_sort_name)
        # if "of" in self.author.split() or "Of" in self.author.split():
        #     self.sort_name = self.author
        # else:
        #     self.sort_name = full_sort_name

        self.sort_title = self.normalize_sort_title(self.title)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class BookImage(models.Model):
    class Meta:
        verbose_name_plural = "Book Images"
        constraints = [
            # single cover per Book (Postgres only for conditional index)
            models.UniqueConstraint(
                fields=['book'],
                condition=models.Q(is_cover=True),
                name='unique_cover_per_book'
            ),
            # single cover per BoxSet
            models.UniqueConstraint(
                fields=['boxset'],
                condition=models.Q(is_cover=True),
                name='unique_cover_per_boxset'
            ),
            # If view_type is set for a box_set, it must be unique (front/back/spine)
            models.UniqueConstraint(
                fields=['boxset', 'view_type'],
                condition=(
                        models.Q(boxset__isnull=False)
                        & models.Q(view_type__in=["front", "back", "spine"])
                ),
                name='unique_boxset_view_type_except_other'
            ),
            # single author per BoxSet
            models.UniqueConstraint(
                fields=['author'],
                condition=models.Q(is_cover=True),
                name='unique_image_per_author'
            ),

        ]

    # ownership - exactly one of these should be set per image
    book = models.ForeignKey(
        "Book",
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True
    )
    spotlight_cover = models.ForeignKey(
        "BookSpotlight",
        on_delete=models.SET_NULL,
        related_name="spotlight_images",
        blank=True,
        null=True
    )
    boxset = models.ForeignKey(
        "BoxSet",
        on_delete=models.CASCADE,
        related_name="boxset_images",
        blank=True,
        null=True
    )
    author = models.ForeignKey(
        "Author",
        on_delete=models.SET_NULL,
        related_name="author_images",
        blank=True,
        null=True
    )

    image = models.ImageField(upload_to="images/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="images/thumbnails/", blank=True,
                                  null=True, editable=False)
    small_thumbnail = models.ImageField(upload_to="images/thumbnails/",
                                      blank=True,
                                  null=True, editable=False)

    # cover flag applies per-owner; only one is_cover=True per Book and per BoxSet
    is_cover = models.BooleanField(default=False)

    # Optional for box set images: front/back/spine (or None)
    VIEW_TYPE_CHOICES = [
        ("left", "Left"),
        ("spine", "Spine"),
        ("right", "Right"),
        ("other", "Other"),
    ]
    view_type = models.CharField(max_length=20, choices=VIEW_TYPE_CHOICES,
                                 blank=True, null=True)

    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        owner = self.book or self.boxset or self.spotlight_cover or self.author
        return f"Image for {getattr(owner, 'title', getattr(owner, 'name', 'Unknown'))}"

    # admin preview
    def thumbnail_preview(self):
        if self.thumbnail:
            return mark_safe(
                f'<img src="{self.thumbnail.url}" width="100" style="border:1px solid #ccc; border-radius:4px;" />'
            )
        if self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="100" style="border:1px solid #ccc; border-radius:4px;" />'
            )
        return "(No image)"

    thumbnail_preview.short_description = "Preview"
    thumbnail_preview.allow_tags = True

    def clean(self):
        # Called by ModelForm/Full clean; ensure exactly one owner is set
        owner_count = sum(
            bool(x) for x in (self.book, self.spotlight_cover, self.boxset,
                self.author))
        if owner_count != 1:
            raise ValidationError(
                "Image must belong to exactly one of: book, spotlight_cover, "
                "box_set, or author.")

    def save(self, *args, **kwargs):
        # Validate ownership at save time (in case full_clean isn't called)
        owner_count = sum(
            bool(x) for x in (self.book, self.spotlight_cover, self.boxset,
                self.author))
        if owner_count != 1:
            raise ValueError(
                "Image must belong to exactly one of: book, spotlight_cover, "
                "box_set, or author.")

        # If this is being set as cover, demote any other covers for that owner
        if self.is_cover:
            if self.book:
                BookImage.objects.filter(book=self.book, is_cover=True).exclude(
                    pk=self.pk).update(is_cover=False)
            if self.boxset:
                BookImage.objects.filter(boxset=self.boxset,
                                         is_cover=True).exclude(
                    pk=self.pk).update(is_cover=False)
            if self.spotlight_cover:
                BookImage.objects.filter(spotlight_cover=self.spotlight_cover,
                                         is_cover=True).exclude(
                    pk=self.pk).update(is_cover=False)
            if self.author:
                BookImage.objects.filter(author=self.author,
                                         is_cover=True).exclude(
                    pk=self.pk).update(is_cover=False)

        # If there's an uploaded image, process it into a main and a thumbnail
        if self.image:
            img = Image.open(self.image)

            # ✅ Apply EXIF orientation (fixes rotated/sideways uploads)
            img = ImageOps.exif_transpose(img)

            # Ensure RGB mode
            if img.mode != "RGB":
                img = img.convert("RGB")

            original_name = os.path.splitext(os.path.basename(self.image.name))[
                0]

            # --- main image (max 1200x1200) ---
            main_img = img.copy()
            main_img.thumbnail((600, 600), Image.Resampling.LANCZOS)
            img_io = BytesIO()
            main_img.save(img_io, format="JPEG", quality=85)
            img_io.seek(0)
            main_filename = f"{original_name}.jpg"
            self.image = InMemoryUploadedFile(
                img_io, 'ImageField', main_filename, "image/jpeg",
                img_io.getbuffer().nbytes, None
            )

            # --- thumbnail (200x200) ---
            thumb_img = img.copy()
            thumb_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            thumb_img.save(thumb_io, format="JPEG", quality=85)
            thumb_io.seek(0)
            thumb_filename = f"{original_name}_thumb.jpg"
            self.thumbnail = InMemoryUploadedFile(
                thumb_io, 'ImageField', thumb_filename, "image/jpeg",
                thumb_io.getbuffer().nbytes, None
            )

            # --- small thumbnail (125x125) ---
            sm_thumb_img = img.copy()
            sm_thumb_img.thumbnail((125, 125), Image.Resampling.LANCZOS)
            sm_thumb_io = BytesIO()
            sm_thumb_img.save(sm_thumb_io, format="JPEG", quality=85)
            sm_thumb_io.seek(0)
            sm_thumb_filename = f"{original_name}_sm_thumb.jpg"
            self.small_thumbnail = InMemoryUploadedFile(
                sm_thumb_io, 'ImageField', sm_thumb_filename, "image/jpeg",
                sm_thumb_io.getbuffer().nbytes, None
            )

        super().save(*args, **kwargs)


class BoxSet(models.Model):
    name = models.CharField(max_length=200)
    isbn10 = models.CharField(max_length=10, blank=True, null=True)
    isbn13 = models.CharField(max_length=13, blank=True, null=True)

    @property
    def cover_image(self):
        return self.boxset_images.filter(is_cover=True).first()

    @property
    def left_image(self):
        return self.boxset_images.filter(view_type='left').first()

    @property
    def spine_image(self):
        return self.boxset_images.filter(view_type='spine').first()

    @property
    def right_image(self):
        return self.boxset_images.filter(view_type='right').first()

    @property
    def other_images(self):
        return self.boxset_images.filter(view_type='other')

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
