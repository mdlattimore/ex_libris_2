# catalog/forms.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Submit, Div
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Volume, Work, Author


class VolumeForm(forms.ModelForm):
    class Meta:
        model = Volume
        fields = [
            'title',
            'collection',
            'works',
            'book_set',
            'volume_number',
            'publisher',
            'publication_date',
            'publication_year',
            'isbn13',
            'isbn10',
            'volume_content_type',
            'volume_edition_type',
            'volume_url',
            'illustrator',
            'edition',
            'description',
            'binding',
            'volume_url',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'cover_url',
            'notes',
            'acquisition_date',
            'acquisition_year',
            'source',
            'price',
            'estimated_value',
            'edition_notes',
            'volume_json',
        ]

        widgets = {
            "volume_json": JSONEditorWidget(
                options={
                    "mode": "code",  # start in "code" view
                    "modes": ["tree", "code"],
                    "search": True,
                }
            ),
        }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper()
    #     self.helper.layout = Layout(
    #         Row(
    #             Column("title", css_class="form-group col-md-4 mb-0")
    #         ),
    #         Row(
    #             Column("collection", css_class="form-group col-md-4 mb-0"),
    #             Column("works", css_class="form-group col-md-4 mb-0"),
    #         ),
    #         Row(
    #             Submit(
    #                 "submit",
    #                 "Save",
    #                 css_class="form-group btn btn-primary col-md-1 mb-0",
    #             ),
    #             HTML('<span class="form-group col-md-3 mb-0"></span>'),
    #
    #     ))


class WorkCreateForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["author"].queryset = Author.objects.order_by("sort_name")

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column("title", css_class="form-group col-md-4 mb-0"),



                    Column("author", css_class="form-group col-md-4 mb-0"),
                    HTML("""
                    <div class="form-group col-md-4 mb-0 d-flex 
                    align-items-center">
                    <a href="#"
                        hx-get="{% url 'author_create' %}"#}
                        hx-target="#author-modal"#}
                        hx-swap="innerHTML"#}
                        class="btn btn-outline-secondary">
                                + Add Author
                    </a>
                    </div>""")
                ),
            Row(
                Column("first_published", css_class="form-group col-md-4 mb-0"),
                Column("work_type", css_class="form-group col-md-4 mb-0"),
                Column("genre", css_class="form-group col-md-4 mb-0"),
            ),

            Row(
                Column("notes", css_class="form-group col-md-4 "
                                                    "mb-0"),

                Column("text", css_class="form-group col-md-8 "
                                          "mb-0"),
            ),
            Row(
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                Submit(
                    "submit",
                    "Save",
                    css_class="form-group btn btn-primary col-md-1 mb-0",
                ),
                HTML('<span class="form-group col-md-3 mb-0"></span>'),
                HTML(
                    '<a href="javascript:javascript:history.go(-1)" class="form-group btn btn-danger col-md-1">Cancel</a>'
                ),
            ),
            Div(id="author-modal"))



class AuthorCreateForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = "__all__"


class ISBNSearchForm(forms.Form):
    isbn = forms.CharField(max_length=14, label='ISBN')
