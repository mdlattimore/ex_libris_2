# pages/models.py
from django.db import models
from django.core.exceptions import ValidationError
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class SiteContent(models.Model):
    home_content = MarkdownxField("Home Page Content", blank=True)
    about_content = MarkdownxField("About Page Content", blank=True)

    # add other static pages as you like ...

    class Meta:
        verbose_name = "Site Content"
        verbose_name_plural = "Site Content"

    def clean(self):
        if SiteContent.objects.exists() and not self.pk:
            raise ValidationError("Only one SiteContent instance is allowed.")

    def __str__(self):
        return "Site Content"

    @property
    def home_html(self):
        return markdownify(self.home_content)

    @property
    def about_html(self):
        return markdownify(self.about_content)

