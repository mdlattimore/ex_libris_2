import json

from django.contrib import admin, messages
from django.utils.safestring import mark_safe

from .models import (Author, Work, BookSet, Volume, AuthorAlias, Collection,
                     Genre, Bibliography, VolumeBibliographyReference)
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
# from .utils.cleanup import find_orphan_images, delete_orphan_images
from markdownx.admin import MarkdownxModelAdmin
from catalog.utils.normalization import normalize_sort_title
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ('name',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['full_name']
    ordering = ('sort_name',)

@admin.register(AuthorAlias)
class AuthorAlias(admin.ModelAdmin):
    list_display = ['alias', 'author']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["name"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "description"]



@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title']
    ordering = ('sort_title',)


@admin.register(BookSet)
class BookSetAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(Bibliography)
class BibliographyAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(VolumeBibliographyReference)
class VolumeBibliographyReferenceAdmin(admin.ModelAdmin):
    list_display = ['volume', 'bibliography', 'reference_detail']

class VolumeBibliographyReferenceInline(admin.TabularInline):
    model = VolumeBibliographyReference
    extra = 1



@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'edition']
    ordering = ('sort_title',)
    inlines = [VolumeBibliographyReferenceInline]
    search_fields = ['title', 'edition']

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget(attrs={"class": "json-wide-editor"})},
    }

    readonly_fields = (
        'pretty_volume_json',)  # Replace 'json_field' with your actual
    # JSONField name

    def pretty_volume_json(self, obj):
        if not obj.volume_json:
            return "(No JSON data)"
        try:
            pretty = json.dumps(obj.volume_json, indent=4, sort_keys=True)
            html = f"""
                <pre style="
                    white-space: pre-wrap;
                    background-color: #f6f8fa;
                    border: 1px solid #ddd;
                    border-radius: 6px;
                    padding: 10px;
                    font-family: monospace;
                    font-size: 13px;
                    line-height: 1.4;
                    overflow-x: auto;
                ">{pretty}</pre>
            """
            return mark_safe(html)  # <— key fix!
        except Exception as e:
            return f"Error formatting JSON: {e}"

    pretty_volume_json.short_description = "Volume JSON"
    # display name
    # 🧭 Jazzmin tabs configuration
    # Define your sections as normal Django fieldsets
    fieldsets = [
        ("Bibliographic", {
            "fields": (
                "title", "collection", "works", "book_set",
            "volume_number",
                "publisher", "publication_year",
                "isbn13", "isbn10", "volume_content_type",
                "volume_edition_type",
                "illustrator", "edition", "description",
            ),
        }),
        ("Description & Condition", {
            "fields": (
                "binding", "condition", "dust_jacket",
                "dust_jacket_condition", "ex_library", "cover_url", "notes",
                "volume_json",
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
