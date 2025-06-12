from django.db import models
from simple_name_parser import NameParser

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

        if self.title.startswith("The "):
            self.sort_title = self.title.lstrip("The ")
        elif self.title.startswith("the "):
            self.sort_title = self.title.lstrip("the ")
        elif self.title.startswith("A "):
            self.sort_title = self.title.lstrip("A ")
        elif self.title.startswith("a "):
            self.sort_title = self.title.lstrip("a ")
        elif self.title.startswith("An "):
            self.sort_title = self.title.lstrip("An ")
        elif self.title.startswith("an "):
            self.sort_title = self.title.lstrip("an ")
        else:
            self.sort_title = self.title
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name