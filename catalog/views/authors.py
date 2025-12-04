from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from catalog.forms import AuthorCreateForm
from catalog.models import Author


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorCreateForm
    success_url = reverse_lazy("author_list")

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["partials/author_create_partial.html"]
        return ["catalog/author_create_update.html"]

    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get("HX-Request"):
            return JsonResponse({
                "id": self.object.id,
                "name": self.object.full_name
            })
        return redirect(self.success_url)

    def form_invalid(self, form):
        if self.request.headers.get("HX-Request"):
            html = render_to_string(
                "partials/author_create_partial.html",
                {"form": form},
                request=self.request
            )
            return JsonResponse({"html": html}, status=400)
        return super().form_invalid(form)


class AuthorCreateModalView(View):
    template_name = "modals/author_form_modal.html"

    def get(self, request, *args, **kwargs):
        form = AuthorCreateForm()
        html = render_to_string(self.template_name, {"form": form},
                                request=request)
        return HttpResponse(html)

    def post(self, request, *args, **kwargs):
        form = AuthorCreateForm(request.POST)
        if form.is_valid():
            author = form.save()

            # Return out-of-band option snippet
            option_html = render_to_string(
                "partials/author_option.html",
                {"author": author},
                request=request,
            )
            return HttpResponse(option_html)

        html = render_to_string(self.template_name, {"form": form},
                                request=request)
        return HttpResponse(html)


class AuthorUpdateView(UpdateView):
    model = Author
    context_object_name = "author"
    template_name = "catalog/author_create_update.html"
    fields = "__all__"


class AuthorListView(ListView):
    model = Author
    context_object_name = 'authors'
    template_name = "catalog/author_list.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorListView, self).get_context_data(**kwargs)
        all_authors = Author.objects.all()
        authors_sorted = sorted(all_authors,
                                key=lambda author: author.sort_name)
        context['authors_display'] = authors_sorted
        return context


class AuthorDetailView(DetailView):
    model = Author
    context_object_name = 'author'
    template_name = "catalog/author_detail.html"
