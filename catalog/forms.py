# catalog/forms.py
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Submit, Div
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from .models import Volume, Work, Author, DevNote

from crispy_forms.layout import Submit, Layout, Row, Column, HTML, Field


class PricingForm(forms.Form):
    MODE_NET = "net"
    MODE_PRICE = "price"
    MODE_CHOICES = [
        (MODE_NET, "Calculate net proceeds from listing price"),
        (MODE_PRICE, "Calculate listing price from desired net proceeds"),
    ]

    mode = forms.ChoiceField(choices=MODE_CHOICES, widget=forms.RadioSelect,
                             label="Calculator Mode")

    input_number = forms.FloatField(
        label="Input",
        help_text="Enter listing price (if calculating net) OR desired net proceeds (if calculating price)."
    )

    tax_rate = forms.FloatField(label="Sales tax (%)", initial=7.5)
    shipping = forms.FloatField(label="Shipping ($)", initial=6.72)
    ebay_comm = forms.FloatField(label="eBay fee (%)", initial=15.3)
    xaction_fee = forms.FloatField(label="Transaction fee ($)", initial=0.30)



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
            'illustrator',
            'edition',
            'description',
            'binding',
            'condition',
            'dust_jacket',
            'dust_jacket_condition',
            'cover_url',
            'notes',
            'acquisition_date',
            'acquisition_year',
            'source',
            'price',
            'acquisition_cost',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['works'].label = "Works (Add Work Button Above)"
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                HTML("""<h5 class="fw-light 
                text-decoration-underline">Bibliographic 
                Information</h5>""")
            ),
            Row(
                Column("title", css_class="form-group col-md-4 mb-0")
            ),
            Row(
                Column("collection", css_class="form-group col-md-3 mb-0"),
                Column("works", css_class="form-group col-md-4 mb-0"),
                Column("book_set", css_class="form-group col-md-3 mb-0"),
                Column("volume_number", css_class="form-group col-md-2 mb-0"),
            ),

            Row(
                Column("publisher", css_class="form-group col-md-4 mb-0"),
                Column("publication_date", css_class="form-group col-md-4 "
                                                     "mb-0"),
                Column("publication_year", css_class="form-group col-md-4 "),
            ),
            Row(
                Column("isbn13", css_class="form-group col-md-4 mb-0"),
                Column("isbn10", css_class="form-group col-md-4 "),
            ),
            Row(
                Column("volume_content_type",
                       css_class="form-group col-md-4 mb-0"),
                Column("volume_edition_type",
                       css_class="form-group col-md-4 mb-0"),
                Column("volume_url", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("edition", css_class="form-group col-md-4 mb-0"),
                Column("illustrator", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("description", css_class="form-group col-md-6 mb-0"),
            ),
            Row(
                HTML("""<h5 class="fw-light 
                        text-decoration-underline">Description and 
                        Condition</h5>""")
            ),
            Row(
                Column("binding", css_class="form-group col-md-3 mb-0"),
                Column("condition", css_class="form-group col-md-3 mb-0"),
                Column("dust_jacket", css_class="form-group col-md-3 mb-0"),
                Column("dust_jacket_condition", css_class="form-group "
                                                          "col-md-3 mb-0"),
            ),
            Row(
                Column("notes", css_class="form-group col-md-6 mb-0"),
                Column("cover_url", css_class="form-group col-md-6 mb-0"),
            ),
            Row(
                HTML("""<h5 class="fw-light">Collection Data<h5> """)
            ),
            Row(
                Column("acquisition_date",
                       css_class="form-group col-md-4 mb-0"),
                Column(
                    "acquisition_year", css_class="form-group col-md-4 mb-0"
                ),
                Column("source", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("price", css_class="form-group col-md-4 mb-0"),
                Column("acquisition_cost", css_class="form-group col-md-4 "
                                                     "mb-0"),

                Column("estimated_value", css_class="form-group col-md-4 mb-0"),
            ),
            Row(
                Column("edition_notes", css_class="form-group col-md-5 mb-0"),
                Column("volume_json", css_class="form-group col-md-7 mb-0"),
            ),

            Row(
                Submit(
                    "submit",
                    "Save",
                    css_class="form-group btn btn-primary col-md-1 mb-0",
                ),
                HTML('<span class="form-group col-md-3 mb-0"></span>'),

            ))


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
                Column("notes", css_class="form-group col-md-6 "
                                          "mb-0"),

                Column("text", css_class="form-group col-md-6 "
                                         "mb-0"),
            ),
            Row(
                Column("work_ebook_url", css_class="form-group col-md-4 mb-0"),
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


class DevNoteCreateForm(forms.ModelForm):
    class Meta:
        model = DevNote
        exclude = ['user', 'referring_url', 'updated_at']