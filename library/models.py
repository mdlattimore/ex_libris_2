from django.db import models
from simple_name_parser import NameParser
from PIL import Image
import sys
import os
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.text import slugify
from django.utils.html import mark_safe

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
    notes = models.TextField(blank=True, null=True)
    sort_name = models.CharField(max_length=150, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Parse full_name into first and last names before saving.
        # The function used (parse_name()) returns a named tuple
        name_parts = parse_name(self.full_name)
        full_sort_name = []
        full_sort_name.append(name_parts.surname)
        full_sort_name.append(name_parts.given_name)
        full_sort_name = " ".join(full_sort_name)
        if "of" in self.full_name.split() or "Of" in self.full_name.split():
            self.sort_name = self.full_name
        else:
            self.sort_name = full_sort_name

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

    # metadata
    collection = models.ForeignKey("Collection", on_delete=models.CASCADE,
                                   related_name="books", blank=True, null=True)
    book_spotlight = models.ForeignKey(BookSpotlight,
                                       on_delete=models.SET_NULL, blank=True,
                                       null=True, related_name="editions")
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=100, blank=True, null=True)
    author = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_date = models.CharField(max_length=50, blank=True, null=True)
    number_of_pages = models.CharField(max_length=10, blank=True, null=True)
    isbn_10 = models.CharField(max_length=15, blank=True, null=True)
    isbn_13 = models.CharField(max_length=20, blank=True, null=True)
    genres = models.ManyToManyField("Genre", related_name="book_genres",
                                    blank=True)
    cover_id = models.CharField(max_length=250, blank=True, null=True)

    # collection data
    owned = models.BooleanField(default=True)
    date_acquired = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=150, blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True,
                                null=True)
    est_value = models.DecimalField(decimal_places=2, max_digits=10, blank=True,
                                null=True)
    notes = models.TextField(blank=True, null=True)
    binding = models.CharField(max_length=30, choices=BINDING_CHOICES,
                               blank=True, null=True)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES,
                                 blank=True, null=True)
    dust_jacket = models.BooleanField(default=False)
    dust_jacket_condition = models.CharField(max_length=30,
                                             choices=CONDITION_CHOICES, blank=True, null=True)
    signed_by_author = models.BooleanField(default=False)
    is_collectible = models.BooleanField(default=False)
    collectible_notes = models.TextField(blank=True, null=True)

    # utility
    sort_name = models.CharField(max_length=150, editable=True)
    sort_title = models.CharField(max_length=150, editable=True)
    google_info = models.CharField(max_length=200, blank=True, null=True)
    book_json = models.TextField(blank=True, null=True)

    @property
    def cover_image(self):
        return self.images.filter(is_cover=True).first()

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
        name_parts = parse_name(self.author)
        full_sort_name = []
        full_sort_name.append(name_parts.surname)
        full_sort_name.append(name_parts.given_name)
        full_sort_name.append(self.title)
        full_sort_name = " ".join(full_sort_name)
        if "of" in self.author.split() or "Of" in self.author.split():
            self.sort_name = self.author
        else:
            self.sort_name = full_sort_name

        self.sort_title = self.normalize_sort_title(self.title)
        # if self.title.startswith("The "):
        #     self.sort_title = self.title.lstrip("The ")
        # elif self.title.startswith("the "):
        #     self.sort_title = self.title.lstrip("the ")
        # elif self.title.startswith("A "):
        #     self.sort_title = self.title.lstrip("A ")
        # elif self.title.startswith("a "):
        #     self.sort_title = self.title.lstrip("a ")
        # elif self.title.startswith("An "):
        #     self.sort_title = self.title.lstrip("An ")
        # elif self.title.startswith("an "):
        #     self.sort_title = self.title.lstrip("an ")
        # else:
        #     self.sort_title = self.title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# class BookImage(models.Model):
#     class Meta:
#         verbose_name_plural = "Book Images"
#         constraints = [
#             models.UniqueConstraint(fields=['book'],
#                                     condition=models.Q(is_book_cover=True),
#                                     name='unique_cover_per_book')
#         ]
#
#
#
#     book = models.ForeignKey(Book, on_delete=models.CASCADE,
#                              related_name="images", blank=True, null=True)
#     spotlight_cover = models.ForeignKey(BookSpotlight,
#                                         on_delete=models.SET_NULL,
#                                         related_name="spotlight_images", blank=True, null=True)
#     image = models.ImageField(upload_to="images/", blank=True, null=True)
#     caption = models.CharField(max_length=200, blank=True, null=True)
#     is_book_cover = models.BooleanField(default=False)
#
#     @property
#     def display_name(self):
#         if self.book:
#             display_name = self.book.title
#         else:
#             display_name = f"{self.spotlight_cover.title} Spotlight"
#
#         return display_name
#
#     def save(self, *args, **kwargs):
#         # Process the image for storage to resize to 200x200
#         if self.image:
#             img = Image.open(self.image)
#
#             # Convert to RGB (prevents errors from PNG/WebP tranparency)
#             if img.mode != "RGB":
#                 img = img.convert("RGB")
#
#             # Resize image while maintaning aspect ratio
#             output_size = (1200, 1200)
#             img.thumbnail(output_size, Image.Resampling.LANCZOS)
#
#             # Save as jpeg with 85% quality
#             img_io = BytesIO()
#             img.save(img_io, format="JPEG", quality=85)
#
#             # Get original filename without extension
#             original_name = os.path.splitext(self.image.name)[0]
#
#             # Generate a new filename with .jpg extension
#             new_filename = f"{original_name}.jpg"
#
#             # Replace the uploaded image with the processed image
#             self.image = InMemoryUploadedFile(
#                 img_io,
#                 'ImageField',
#                 new_filename,
#                 "image/jpeg",
#                 sys.getsizeof(img_io),
#                 None,
#             )
#
#         super().save(*args, **kwargs)
#
#
#
#     def __str__(self):
#         try:
#             return f"Image for {self.book.title}."
#         except AttributeError:
#             return f"Image for {self.spotlight_cover.title}."

class BookImage(models.Model):
    class Meta:
        verbose_name_plural = "Book Images"
        constraints = [
            models.UniqueConstraint(
                fields=['book'],
                condition=models.Q(is_cover=True),
                name='unique_cover_per_book'
            )
        ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="images",
        blank=True,
        null=True
    )
    spotlight_cover = models.ForeignKey(
        BookSpotlight,
        on_delete=models.SET_NULL,
        related_name="spotlight_images",
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to="images/thumbnails/", blank=True, null=True, editable=False)
    caption = models.CharField(max_length=200, blank=True, null=True)
    is_cover = models.BooleanField(default=False)

    @property
    def display_name(self):
        if self.book:
            return self.book.title
        return f"{self.spotlight_cover.title} Spotlight"

    def save(self, *args, **kwargs):
        # --- Ensure only one cover per book ---
        if self.is_cover and self.book:
            BookImage.objects.filter(book=self.book, is_cover=True).exclude(pk=self.pk).update(is_cover=False)

        if self.image:
            img = Image.open(self.image)

            # Convert to RGB (prevents errors from PNG/WebP transparency)
            if img.mode != "RGB":
                img = img.convert("RGB")

            # --- Resize main image (max 1200x1200) ---
            main_img = img.copy()
            main_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
            img_io = BytesIO()
            main_img.save(img_io, format="JPEG", quality=85)
            original_name = os.path.splitext(self.image.name)[0]
            new_filename = f"{original_name}.jpg"
            self.image = InMemoryUploadedFile(
                img_io, 'ImageField', new_filename, "image/jpeg", img_io.getbuffer().nbytes, None
            )

            # --- Create thumbnail (200x200) ---
            thumb_img = img.copy()
            thumb_img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            thumb_io = BytesIO()
            thumb_img.save(thumb_io, format="JPEG", quality=85)
            thumb_filename = f"{original_name}_thumb.jpg"
            self.thumbnail = InMemoryUploadedFile(
                thumb_io, 'ImageField', thumb_filename, "image/jpeg", thumb_io.getbuffer().nbytes, None
            )

        super().save(*args, **kwargs)

    def thumbnail_preview(self):
        """Returns an HTML img tag for admin preview."""
        if self.thumbnail:
            return mark_safe(
                f'<img src="{self.thumbnail.url}" width="100" style="border:1px solid #ccc; border-radius:4px;" />')
        elif self.image:
            return mark_safe(
                f'<img src="{self.image.url}" width="100" style="border:1px solid #ccc; border-radius:4px;" />')
        return "(No image)"

    thumbnail_preview.short_description = "Preview"
    thumbnail_preview.allow_tags = True

    def __str__(self):
        if self.book:
            return f"Image for {self.book.title}"
        return f"Image for {self.spotlight_cover.title}"


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


