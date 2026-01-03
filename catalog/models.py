from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from simple_name_parser import NameParser

from catalog.integrations.google_books_provider import GoogleBooksProvider
from catalog.utils.fuzzy_matching import normalize_name
from catalog.utils.normalization import normalize_sort_title

parser = NameParser()
parse_name = parser.parse_name


# ---- 1. Author -----------------------------------------


class Author(models.Model):
    full_name = models.CharField(max_length=200, unique=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    dod = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    author_image_url = models.URLField(blank=True, null=True)
    bio = MarkdownxField(blank=True, null=True)
    sort_name = models.CharField(max_length=150, blank=True, null=True)
    match_name = models.CharField(max_length=150, blank=True, null=True,
                                  unique=True)
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    @property
    def bio_html(self):
        return markdownify(self.bio)

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
        elif self.first_name == "Unknown":
            self.sort_name = "ZZ Author"
        elif self.last_name == "Various":
            self.sort_name = "Z Author"
        else:
            self.sort_name = full_sort_name
        self.match_name = normalize_name(self.full_name)
        if not self.slug:
            base = slugify(self.full_name)
            slug = base
            counter = 1

            while Author.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("author_detail", args=[self.slug])

    class Meta:
        ordering = ['sort_name']

    def __str__(self):
        return self.full_name


class AuthorAlias(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='aliases')
    alias = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "aliases"

    def __str__(self):
        return f"{self.alias} = {self.author.full_name}"


# --------- 1.5 Genre ----------------------------------
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# -------- 2. Work -----------------------------------------

class Work(models.Model):

    WORK_TYPE_CHOICES = [
        ("NOVEL", "Novel"),
        ("NOVELLA", "Novella"),
        ("SHORT_STORY", "Short Story"),
        ("STORY_CYCLE", "Story Cycle"),
        ("POEM", "Poem"),
        ("POETRY_COLLECTION", "Poetry Collection"),
        ("PLAY", "Play / Drama"),
        ("ESSAY", "Essay"),
        ("ESSAY_COLLECTION", "Essay Collection"),
        ("NONFICTION", "Non-Fiction Work"),
        ("TRANSLATION", "Translation"),
        ("COMPOSITE", "Composite / Edited Work"),
        ("ANTHOLOGY", "Anthology (Multiple Authors)"),
        ("CRITICISM", "Criticism / Commentary"),
        ("SONG_CYCLE", "Song Cycle"),
        ("REFERENCE_WORK", "Reference Work"),
        ("OTHER", "Other"),
    ]

    title = models.CharField(max_length=255)
    sort_title = models.CharField(max_length=255, blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE,
                               related_name='works')
    first_published = models.IntegerField(blank=True, null=True)
    work_type = models.CharField(
        max_length=50,
        # choices=WorkType.choices,
        # default=WorkType.NOVEL
        choices=WORK_TYPE_CHOICES,
        blank=True, null=True
    )
    genre = models.ManyToManyField(Genre, related_name="works", blank=True)

    notes = MarkdownxField(blank=True, null=True)
    text = MarkdownxField(blank=True, null=True)
    slug = models.SlugField(max_length=120, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.sort_title = normalize_sort_title(self.title)
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1

            while Work.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['sort_title']

    @property
    def kind(self):
        return "Work"

    @property
    def work_notes_html(self):
        if not self.notes:
            return ""
        return markdownify(self.notes)

    @property
    def work_text_html(self):
        return markdownify(self.text)

    def get_absolute_url(self):
        return reverse("work_detail", args=[self.slug])

    def __str__(self):
        return self.title


# -------- 3. BookSet -------------------------------------

class BookSet(models.Model):
    CONDITION_CHOICES = [
        ("AN", "As New"),
        ("FI", "Fine"),
        ("NF", "Near Fine"),
        ("VG", "Very Good"),
        ("GO", "Good"),
        ("FA", "Fair"),
        ("RC", "Reading Copy")
    ]
    title = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    isbn13 = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        help_text="13-digit ISBN (normalized)."
    )
    isbn10 = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="10-digit ISBN (legacy, optional)."
    )
    illustrator = models.CharField(max_length=255, blank=True)
    total_volumes = models.IntegerField(blank=True, null=True)
    is_box_set = models.BooleanField(default=False)
    boxset_case_condition = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=CONDITION_CHOICES,
    )
    description = MarkdownxField(blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)
    acquisition_year = models.IntegerField(blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True,
                                null=True)
    cover_url = models.URLField(blank=True, null=True)
    notes = MarkdownxField(blank=True, null=True)
    sort_title = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True, null=True)

    class Meta:
        ordering = ['title']

    @property
    def kind(self):
        return "BookSet"

    @property
    def bookset_description_html(self):
        return markdownify(self.description)

    def save(self, *args, **kwargs):
        if not self.cover_url and (self.isbn13 or self.isbn10):
            set_lookup = GoogleBooksProvider()
            if self.isbn13:
                book = set_lookup.lookup(self.isbn13)
            else:
                book = set_lookup.lookup(self.isbn10)
            self.cover_url = book["cover_url"]
            print(self.cover_url)

        self.sort_title = normalize_sort_title(self.title)

        super().save(*args, **kwargs)

        if self.isbn10 and not self.isbn13:
            self.isbn13 = self.convert_isbn10_to_13(self.isbn10)
        elif self.isbn13 and not self.isbn10:
            maybe10 = self.convert_isbn13_to_10(self.isbn13)
            if maybe10:
                self.isbn10 = maybe10
        self.sort_title = normalize_sort_title(self.title)
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1

            while BookSet.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # ISBN conversion functions ISBN10 to 13 and ISBN13 to 10
    @staticmethod
    def convert_isbn10_to_13(isbn10: str) -> str:
        """Return ISBN-13 string given a 10-digit ISBN."""
        isbn10 = isbn10.replace("-", "").strip()
        core = "978" + isbn10[:-1]
        total = sum(
            (1 if i % 2 == 0 else 3) * int(x) for i, x in enumerate(core))
        check = (10 - (total % 10)) % 10
        return core + str(check)

    @staticmethod
    def convert_isbn13_to_10(isbn13: str) -> str | None:
        """Return ISBN-10 string given a 13-digit ISBN (if prefix 978)."""
        isbn13 = isbn13.replace("-", "").strip()
        if not isbn13.startswith("978"):
            return None
        core = isbn13[3:-1]
        total = sum((10 - i) * int(x) for i, x in enumerate(core))
        check = 11 - (total % 11)
        check_digit = "X" if check == 10 else "0" if check == 11 else str(check)
        return core + check_digit

    def get_absolute_url(self):
        return reverse("bookset_detail", args=[self.slug])

    def __str__(self):
        return self.title


# ------ 3.5 Collection ----------------------------
class Collection(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True, null=True)
    description = MarkdownxField(blank=True, null=True)

    @property
    def description_html(self):
        return markdownify(self.description)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1

            while Collection.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("collection_detail", args=[self.slug])

    def __str__(self):
        return self.name


# ----- 3.75 ----------------------------------------------

class Bibliography(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=200, blank=True, null=True)
    edition = models.CharField(max_length=200, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.title}"


# ------ 4. Volume ----------------------------------------

class Volume(models.Model):
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
    VOLUME_CONTENT_TYPE_CHOICES = [
        ("SINGLE", "Single Work"),
        ("COLLECTION_SINGLE_AUTHOR", "Collection (One Author)"),
        ("ANTHOLOGY", "Anthology (Multiple Authors)"),
        ("COMPOSITE", "Composite / Edited Volume"),
        ("CRITICAL", "Critical / Commentary Edition"),
        ("REFERENCE", "Reference Work"),
        ("OTHER", "Other"),
    ]
    VOLUME_EDITION_TYPE_CHOICES = [
        ("STANDARD", "Standard Edition"),
        ("COLLECTOR", "Collector's Edition"),
        ("DELUXE", "Deluxe Edition"),
        ("ILLUSTRATED", "Illustrated Edition"),
        ("FACSIMILE", "Facsimile Edition"),
        ("REVISED", "Revised Edition"),
        ("LIMITED", "Limited Edition"),
        ("BOOK_CLUB", "Book Club"),
        ("SLIPCASED", "Slipcased Edition"),
        ("TEXTBOOK", "Textbook / Academic Edition"),
        ("POCKET", "Pocket Edition"),
        ("TRANSLATION", "Translation"),
        ("MUSIC", "Music Notation with Lyrics"),
        ("OTHER", "Other"),
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

    # Bibliographic Information
    title = models.CharField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    collection = models.ManyToManyField(Collection, related_name="volumes",
                                        blank=True)
    sort_title = models.CharField(max_length=255, editable=False, blank=True)
    works = models.ManyToManyField(Work, related_name='volumes', blank=True)
    book_set = models.ForeignKey(BookSet, on_delete=models.CASCADE,
                                 related_name='volumes', blank=True, null=True)
    volume_number = models.PositiveIntegerField(blank=True, null=True)
    publisher = models.CharField(max_length=200, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    isbn13 = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        help_text="13-digit ISBN (normalized)."
    )
    isbn10 = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="10-digit ISBN (legacy, optional)."
    )
    volume_content_type = models.CharField(max_length=50,
                                           choices=VOLUME_CONTENT_TYPE_CHOICES,
                                           blank=True, null=True)
    volume_edition_type = models.CharField(max_length=50,
                                           choices=VOLUME_EDITION_TYPE_CHOICES,
                                           blank=True, null=True)
    volume_url = models.URLField(blank=True, null=True, help_text="URL to "
                                                                  "ebook")
    illustrator = models.CharField(max_length=200, blank=True, null=True)
    edition = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    bibliographies = models.ManyToManyField(
        Bibliography,
        through="VolumeBibliographyReference",
        related_name="volumes",
        blank=True)

    # Description and Condition
    binding = models.CharField(choices=BINDING_CHOICES, max_length=30,
                               blank=True, null=True)
    condition = models.CharField(choices=CONDITION_CHOICES, max_length=30,
                                 blank=True, null=True)
    dust_jacket = models.BooleanField(default=False)
    dust_jacket_condition = models.CharField(choices=CONDITION_CHOICES,
                                             max_length=30, blank=True,
                                             null=True)
    ex_library = models.BooleanField(default=False)
    cover_url = models.URLField(blank=True, null=True)
    notes = MarkdownxField(blank=True, null=True)
    volume_json = models.JSONField(blank=True, null=True)

    # Collection Data
    status = models.CharField(choices=STATUS_CHOICES, max_length=30,
                              default="Catalog", blank=True, null=True)
    acquisition_date = models.DateField(blank=True, null=True)
    acquisition_year = models.IntegerField(blank=True, null=True)
    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True,
                                null=True, default=0)
    acquisition_cost = models.DecimalField(decimal_places=2, max_digits=10,
                                           blank=True, null=True,
                                           default=0)

    estimated_value = models.DecimalField(decimal_places=2, max_digits=10,
                                          blank=True, null=True)
    edition_notes = MarkdownxField(blank=True, null=True)

    # Disposition
    disposition = models.CharField(choices=DISPOSITION_CHOICES,
                                   max_length=30, blank=True, null=True)
    recipient = models.CharField(max_length=150, blank=True, null=True)
    sales_price = models.DecimalField(decimal_places=2, max_digits=10,
                                      blank=True, null=True)
    shipping_charged = models.DecimalField(decimal_places=2, max_digits=10,
                                           blank=True, null=True)
    shipping_cost = models.DecimalField(decimal_places=2, max_digits=10,
                                        blank=True, null=True)
    disposition_date = models.DateField(blank=True, null=True)

    # Utility
    slug = models.SlugField(max_length=255, blank=True, unique=True)

    class Meta:
        ordering = ["sort_title"]

    def __str__(self):
        if self.book_set:
            if self.volume_number:
                return (f"{self.title} (Part of '{self.book_set.title}' Set, "
                        f"Vol. {self.volume_number})")
            else:
                return f"{self.title} (Part of '{self.book_set.title}' Set)"
        else:
            return f"{self.title}"

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

    def save(self, *args, **kwargs):
        if self.isbn10 and not self.isbn13:
            self.isbn13 = self.convert_isbn10_to_13(self.isbn10)
        elif self.isbn13 and not self.isbn10:
            maybe10 = self.convert_isbn13_to_10(self.isbn13)
            if maybe10:
                self.isbn10 = maybe10
        self.sort_title = normalize_sort_title(self.title)
        # handle volumes already existing when acquisition_cost added to model
        if self.acquisition_cost is None:
            self.acquisition_cost = 0

        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1

            while Volume.objects.filter(slug=slug).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    # ISBN conversion functions ISBN10 to 13 and ISBN13 to 10
    @staticmethod
    def convert_isbn10_to_13(isbn10: str) -> str:
        """Return ISBN-13 string given a 10-digit ISBN."""
        isbn10 = isbn10.replace("-", "").strip()
        core = "978" + isbn10[:-1]
        total = sum(
            (1 if i % 2 == 0 else 3) * int(x) for i, x in enumerate(core))
        check = (10 - (total % 10)) % 10
        return core + str(check)

    @staticmethod
    def convert_isbn13_to_10(isbn13: str) -> str | None:
        """Return ISBN-10 string given a 13-digit ISBN (if prefix 978)."""
        isbn13 = isbn13.replace("-", "").strip()
        if not isbn13.startswith("978"):
            return None
        core = isbn13[3:-1]
        total = sum((10 - i) * int(x) for i, x in enumerate(core))
        check = 11 - (total % 11)
        check_digit = "X" if check == 10 else "0" if check == 11 else str(check)
        return core + check_digit

    @property
    def notes_html(self):
        return markdownify(self.notes)

    @property
    def edition_notes_html(self):
        return markdownify(self.edition_notes)

    def get_absolute_url(self):
        return reverse("volume_detail", args=[self.slug])


# ----- 5 Bibliography Reference ----------------------------
class VolumeBibliographyReference(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE,
                               related_name="bibliography_refs")
    bibliography = models.ForeignKey(Bibliography, on_delete=models.CASCADE)
    reference_detail = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="e.g. page 56, entry A2b, plate VIII, etc."
    )

    class Meta:
        unique_together = ("volume", "bibliography", "reference_detail")

    def __str__(self):
        return f"{self.bibliography.code}: {self.reference_detail}"
