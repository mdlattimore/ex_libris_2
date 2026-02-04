import json

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from .models import (Author, Work, BookSet, Volume, AuthorAlias, Bookshelf,
                     Genre, Bibliography, VolumeBibliographyReference,
                     VolumeImage, BooksetImage, DevNote, Collection)
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
# from .utils.cleanup import find_orphan_images, delete_orphan_images
from markdownx.admin import MarkdownxModelAdmin
from catalog.utils.normalization import normalize_sort_title
from django.db import models
from django_json_widget.widgets import JSONEditorWidget


@admin.register(Bookshelf)
class BookshelfAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ('name',)

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


class AddToCollectionForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    collection = forms.ModelChoiceField(
        queryset=Collection.objects.order_by("name"),
        label="Collection",
    )



@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    ordering = ('sort_title',)
    search_fields = ('title',)
    filter_horizontal = ("collections",)

    actions = ["add_to_collection_bulk"]

    def add_to_collection_bulk(self, request, queryset):
        if "apply" in request.POST:
            form = AddToCollectionForm(request.POST)
            if form.is_valid():
                collection = form.cleaned_data["collection"]

                for work in queryset:
                    work.collections.add(collection)

                self.message_user(
                    request,
                    f"Added {queryset.count()} works to collection “{collection.name}”.",
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect(request.get_full_path())

        form = AddToCollectionForm(
            initial={
                "_selected_action": [str(w.pk) for w in queryset],
            }
        )

        return render(
            request,
            "admin/catalog/work/add_to_collection.html",
            {
                "works": queryset,
                "form": form,
                "title": "Add selected works to collection",
                "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            },
        )

    add_to_collection_bulk.short_description = "Add selected works to collection…"

class BooksetImageInline(admin.TabularInline):
    model = BooksetImage
    extra = 0
    fields = ("preview", "kind", "caption", "sort_order", "image_thumb", "image_display", "image_detail")
    readonly_fields = ("preview",)
    ordering = ("sort_order", "created_at")

    def preview(self, obj):
        return thumb_preview(obj, "image_thumb", size=60)
    preview.short_description = "Thumb"


@admin.register(BookSet)
class BookSetAdmin(admin.ModelAdmin):
    list_display = ['title']
    inlines = [BooksetImageInline]

@admin.register(Bibliography)
class BibliographyAdmin(admin.ModelAdmin):
    list_display = ['title']

@admin.register(VolumeBibliographyReference)
class VolumeBibliographyReferenceAdmin(admin.ModelAdmin):
    list_display = ['volume', 'bibliography', 'reference_detail']

class VolumeBibliographyReferenceInline(admin.TabularInline):
    model = VolumeBibliographyReference
    extra = 1



class VolumeImageInline(admin.TabularInline):
    model = VolumeImage
    extra = 0
    fields = ("preview", "kind", "caption", "sort_order", "image_thumb", "image_display", "image_detail")
    readonly_fields = ("preview",)
    ordering = ("sort_order", "created_at")

    def preview(self, obj):
        return thumb_preview(obj, "image_thumb", size=60)
    preview.short_description = "Thumb"


class AddToBookshelfForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    bookshelf = forms.ModelChoiceField(
        queryset=Bookshelf.objects.order_by("name"),
        label="Bookshelf",
    )



@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'edition']
    ordering = ('sort_title',)
    inlines = [VolumeBibliographyReferenceInline, VolumeImageInline]
    search_fields = ['title', 'edition']
    filter_horizontal = ("bookshelves",)  # <-- your M2M field name

    formfield_overrides = {
        models.JSONField: {"widget": JSONEditorWidget(attrs={"class": "json-wide-editor"})},
    }

    readonly_fields = (
        'pretty_volume_json',)  # Replace 'json_field' with your actual
    # JSONField name

    actions = ["add_to_bookshelf_bulk"]

    def add_to_bookshelf_bulk(self, request, queryset):
        if "apply" in request.POST:
            form = AddToBookshelfForm(request.POST)
            if form.is_valid():
                shelf = form.cleaned_data["bookshelf"]

                for volume in queryset:
                    volume.bookshelves.add(shelf)

                self.message_user(
                    request,
                    f"Added {queryset.count()} volumes to bookshelf “{shelf.name}”.",
                    level=messages.SUCCESS,
                )
                return HttpResponseRedirect(request.get_full_path())

        form = AddToBookshelfForm(
            initial={
                "_selected_action": [str(v.pk) for v in queryset],
            }
        )

        return render(
            request,
            "admin/catalog/volume/add_to_bookshelf.html",
            {
                "volumes": queryset,
                "form": form,
                "title": "Add selected volumes to bookshelf",
                "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
            },
        )

    add_to_bookshelf_bulk.short_description = "Add selected volumes to bookshelf…"


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

    def cover_admin_preview(self, obj):
        if obj.cover_image_id:
            return thumb_preview(obj.cover_image, "image_thumb", size=45)
        # fall back to stock cover_url if you want
        return "—"

    cover_admin_preview.short_description = "Cover"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "cover_image":
            # When editing an existing Volume, limit cover choices to its images
            # URL will look like /admin/catalog/volume/<id>/change/
            try:
                object_id = request.resolver_match.kwargs.get("object_id")
            except Exception:
                object_id = None

            if object_id:
                field.queryset = VolumeImage.objects.filter(volume_id=object_id).order_by("sort_order", "created_at")
            else:
                field.queryset = VolumeImage.objects.none()

        return field


    # display name
    # 🧭 Jazzmin tabs configuration
    # Define your sections as normal Django fieldsets
    fieldsets = [
        ("Bibliographic", {
            "fields": (
                "title", "bookshelves", "works", "primary_work", "book_set",
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
                "dust_jacket_condition", "ex_library",
                "cover_image", "cover_url", "notes",
                "volume_json",
            ),
        }),
        ("Collection Data", {
            "fields": ("acquisition_date", "acquisition_year", "source",
                "price", "estimated_value", "edition_notes",),
        }),
        ("Disposition", {
            "fields": ("disposition", "recipient", "sales_price",
                "shipping_charged", "shipping_cost", "disposition_date")
        }),
    ]

    # 👇 THIS is the key line that tells Jazzmin to render tabs
    tabs = True


def thumb_preview(obj, field_name="image_thumb", size=80):
    f = getattr(obj, field_name, None)
    if not f:
        return "—"
    try:
        return format_html(
            '<img src="{}" style="height:{}px;width:auto;border-radius:6px;" />',
            f.url,
            size,
        )
    except Exception:
        return "—"

@admin.register(VolumeImage)
class VolumeImageAdmin(admin.ModelAdmin):
    list_display = ("id", "volume", "kind", "sort_order", "preview_small", "created_at")
    list_filter = ("kind",)
    search_fields = ("volume__title", "caption")
    ordering = ("volume", "sort_order", "created_at")
    readonly_fields = ("preview_large",)

    def preview_small(self, obj):
        return thumb_preview(obj, "image_thumb", size=45)
    preview_small.short_description = "Thumb"

    def preview_large(self, obj):
        return thumb_preview(obj, "image_display", size=250)
    preview_large.short_description = "Preview"


@admin.register(BooksetImage)
class BooksetImageAdmin(admin.ModelAdmin):
    list_display = ("id", "bookset", "kind", "sort_order", "preview_small",
        "created_at")
    list_filter = ("kind",)
    search_fields = ("bookset__title", "caption")
    ordering = ("bookset", "sort_order", "created_at")
    readonly_fields = ("preview_large",)

    def preview_small(self, obj):
        return thumb_preview(obj, "image_thumb", size=45)
    preview_small.short_description = "Thumb"

    def preview_large(self, obj):
        return thumb_preview(obj, "image_display", size=250)
    preview_large.short_description = "Preview"


@admin.register(DevNote)
class DevNoteAdmin(admin.ModelAdmin):
    exclude = ("user",)
    readonly_fields = ("created_at",)
    list_display = ("created_at", "user", "short_notes")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description="Notes")
    def short_notes(self, obj):
        return obj.note[:60]



