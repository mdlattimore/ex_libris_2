from django.contrib import admin
from .models import Book, Genre, BookImage, Collection, BookSpotlight # , Author

class BookSpotlightAdmin(admin.ModelAdmin):
    model = BookSpotlight
    list_display = ['title', ]


class BookInline(admin.TabularInline):
    model = Book.genres.through  # ✅ Works for Many-to-Many Collection-Book
    extra = 0
    readonly_fields = ['book']


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1
    fields = ("thumbnail_preview", "image", "caption", "is_cover")
    readonly_fields = ("thumbnail_preview",)


class BookAdmin(admin.ModelAdmin):
    list_display = ['display_title', 'collectible_notes','display_author',
        'publication_date']
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
    list_display = ("display_name", "is_cover", "thumbnail_preview")
    readonly_fields = ("thumbnail_preview",)

class CategoryAdmin(admin.ModelAdmin):
    model = Collection


admin.site.register(Book, BookAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(BookImage, BookImageAdmin)
admin.site.register(Collection, CategoryAdmin)
admin.site.register(BookSpotlight, BookSpotlightAdmin)
# admin.site.register(Author, AuthorAdmin)
