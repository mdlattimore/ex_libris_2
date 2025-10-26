# pages/admin.py
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import SiteContent

@admin.register(SiteContent)
class SiteContentAdmin(MarkdownxModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                "home_content",
                "about_content",
                # add others as needed
            ),
            "description": "Edit Markdown content for each static page."
        }),
    )

    def has_add_permission(self, request):
        # Prevent creation of more than one row
        return not SiteContent.objects.exists()

