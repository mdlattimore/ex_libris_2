import json

from django import forms
from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from .models import (ReadingPath, ReadingPathItem)
from django.urls import path
from django.shortcuts import redirect, render
from django.utils.html import format_html
# from .utils.cleanup import find_orphan_images, delete_orphan_images
from markdownx.admin import MarkdownxModelAdmin
from catalog.utils.normalization import normalize_sort_title
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

@admin.register(ReadingPath)
class ReadingPathAdmin(admin.ModelAdmin):
    list_display = ['name']
    ordering = ('name',)

@admin.register(ReadingPathItem)
class ReadingPathItemAdmin(admin.ModelAdmin):
    list_display = ['reading_path', 'work']
    ordering = ('work',)