from django.contrib import admin, messages
from .models import Book, Genre, BookImage, Collection, BookSpotlight, \
    BoxSet, Author, AuthorAlias
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
from .utils.cleanup import find_orphan_images, delete_orphan_images
from markdownx.admin import MarkdownxModelAdmin


class BookSpotlightAdmin(admin.ModelAdmin):
    model = BookSpotlight
    list_display = ['title', ]


class BookInline(admin.TabularInline):
    model = Book.genres.through  # ✅ Works for Many-to-Many Collection-Book
    extra = 0
    readonly_fields = ['book']

class BooksByAuthorInline(admin.TabularInline):
    model = Book
    extra = 0



class AuthorAliasAdmin(admin.ModelAdmin):
    model = AuthorAlias
    list_display = [
        'alias',
        'author'
    ]

class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ("thumbnail_preview", "image", "caption", "is_cover", "view_type")
    readonly_fields = ("thumbnail_preview",)


class AuthorAdmin(MarkdownxModelAdmin):
    model = Author
    list_display = ['full_name',]
    ordering = ('last_name', 'first_name')
    inlines = [BooksByAuthorInline, BookImageInline]


class BookAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'collectibility_notes', 'display_author',
        'publication_date', 'id']
    ordering = ('sort_title',)
    readonly_fields = ('id',)
    filter_horizontal = ('genres',)  # ✅ Works in BookAdmin
    inlines = [BookImageInline]


    def display_title(self, obj):
        return obj.title

    def display_author(self, obj):
        return obj.author

    display_title.admin_order_field = "sort_title"
    display_title.short_description = "Title"
    display_author.admin_order_field = "sort_name"
    display_author.short_description = "Author"


# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ['name']

class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    inlines = [
        BookInline]  # ✅ Works because Book.collections.through links to Collection
    ordering = ['name']

# class BookImageAdmin(admin.ModelAdmin):
#     model = BookImage
#     list_display = ['display_name', 'image']

class BookImageAdmin(admin.ModelAdmin):
    list_display = ("caption", "is_cover", "thumbnail_preview")
    readonly_fields = ("thumbnail_preview",)

    change_list_template = "admin/catalog/bookimage_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("cleanup-orphans/",
                 self.admin_site.admin_view(self.cleanup_orphans_view),
                 name="bookimage_cleanup_orphans"),
        ]
        return custom_urls + urls

    def cleanup_orphans_view(self, request):
        """Custom admin view for cleaning up orphan image files."""
        orphaned_files = find_orphan_images()

        if request.method == "POST":
            delete_orphan_images(orphaned_files)
            self.message_user(request,
                              f"Deleted {len(orphaned_files)} orphaned files.",
                              messages.SUCCESS)
            return redirect("..")

        context = {
            **self.admin_site.each_context(request),
            "title": "Clean Up Orphan Images",
            "orphaned_files": orphaned_files,
        }
        return render(request, "admin/catalog/cleanup_orphans.html", context)

class CategoryAdmin(admin.ModelAdmin):
    model = Collection

class BoxSetAdmin(admin.ModelAdmin):
    list_display = ("name", "isbn10", "isbn13", "id")
    inlines = [BookImageInline]  # same inline works for boxset; view_type shows in inline


admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(BookImage, BookImageAdmin)
admin.site.register(Collection, CategoryAdmin)
admin.site.register(BookSpotlight, BookSpotlightAdmin)
admin.site.register(BoxSet, BoxSetAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(AuthorAlias, AuthorAliasAdmin)
