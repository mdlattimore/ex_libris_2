from django.contrib import admin, messages
from .models import Author, Work, BookSet, Volume
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
# from .utils.cleanup import find_orphan_images, delete_orphan_images
from markdownx.admin import MarkdownxModelAdmin


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['full_name']


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(BookSet)
class BookSetAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'edition']
    # 🧭 Jazzmin tabs configuration
    # Define your sections as normal Django fieldsets
    fieldsets = [
        ("Bibliographic", {
            "fields": (
                "title", "works", "book_set", "volume_number",
                "publisher", "publication_year",
                "isbn13", "isbn10",
                "illustrator", "edition",
            ),
        }),
        ("Description & Condition", {
            "fields": (
                "binding", "condition", "dust_jacket",
                "dust_jacket_condition", "notes",
            ),
        }),
        ("Collection Data", {
            "fields": ("acquisition_date", "acquisition_year", "source",
                "price", "estimated_value", "edition_notes",),
        }),
        ("Disposition", {
            "fields": ()
        })
    ]

    # 👇 THIS is the key line that tells Jazzmin to render tabs
    tabs = True
