from django.db.models.functions import Coalesce
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from catalog.forms import DevNoteCreateForm
from catalog.models import DevNote
from urllib.parse import urlparse
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.http import HttpResponse
from django.template.loader import render_to_string


class DevNoteCreateView(LoginRequiredMixin, CreateView):
    model = DevNote
    form_class = DevNoteCreateForm
    template_name = "catalog/dev_note_create.html"
    partial_template_name = "partials/dev_note_form.html"

    def _is_htmx(self):
        return self.request.headers.get("HX-Request") == "true"

    def get_template_names(self):
        if self._is_htmx():
            return [self.partial_template_name]
        return [self.template_name]

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.referring_url = self._get_referring_url()
        response = super().form_valid(form)

        if self._is_htmx():
            # Return a small fragment that closes the modal.
            # (You can also trigger events here; see below.)
            html = """
            <div class="text-success">Saved.</div>
            <script>
              (function () {
                const el = document.getElementById('devNoteModal');
                const modal = bootstrap.Modal.getInstance(el);
                if (modal) modal.hide();
              })();
            </script>
            """
            return HttpResponse(html)

        return response

    def form_invalid(self, form):
        if self._is_htmx():
            html = render_to_string(
                self.partial_template_name,
                {"form": form, "request": self.request},
            )
            return HttpResponse(html, status=422)
        return super().form_invalid(form)

    def get_success_url(self):
        nxt = self.request.GET.get("next") or self.request.POST.get("next")
        return nxt if nxt and nxt.startswith("/") and not nxt.startswith("//") else "/"

    def _get_referring_url(self):
        # Prefer explicit ?next=
        nxt = self.request.GET.get("next") or self.request.POST.get("next")
        if nxt and nxt.startswith("/") and not nxt.startswith("//"):
            return self.request.build_absolute_uri(nxt)

        # Fallback to HTTP_REFERER
        ref = self.request.META.get("HTTP_REFERER")
        if ref:
            return ref

        return ""

    def _is_safe_local_url(self, url: str) -> bool:
        # simple “same-site only” check to avoid open redirects
        return url.startswith("/") and not url.startswith("//")



class DevNoteListView(LoginRequiredMixin, ListView):
    model = DevNote
    template_name = "catalog/dev_note_list.html"
    context_object_name = "dev_notes"

    def get_queryset(self):
        return (
            DevNote.objects
            .annotate(effective_date=Coalesce("updated_at", "created_at"))
            .order_by("-effective_date")
        )


class DevNoteDetailView(LoginRequiredMixin, DetailView):
    model = DevNote
    template_name = "catalog/dev_note_detail.html"
    context_object_name = "dev_note"


# class DevNoteUpdateView(LoginRequiredMixin, UpdateView):
#     model = DevNote
#     form_class = DevNoteCreateForm
#     template_name = "catalog/dev_note_create.html"

# class DevNoteUpdateView(LoginRequiredMixin, UpdateView):
#     model = DevNote
#     form_class = DevNoteCreateForm
#     template_name = "catalog/dev_note_update.html"
#     fallback_url = reverse_lazy("dev_note_list")  # set to something real
#
#     def get_success_url(self):
#         # go back to where you came from (same pattern as create)
#         nxt = self.request.GET.get("next") or self.request.POST.get("next")
#         return nxt if nxt and nxt.startswith("/") and not nxt.startswith("//") else str(self.fallback_url)
#
#     def form_valid(self, form):
#         # If you add any custom logic here, you MUST return the super response
#         return super().form_valid(form)

class DevNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = DevNote
    context_object_name = "dev_note"
    template_name = "catalog/dev_note_update.html"
    fields = ["subject", "note"]
    def get_success_url(self):
        return reverse("dev_note_detail", kwargs={"pk": self.object.pk})
    # fallback_url = reverse_lazy("dev_note_list")  # set to something real
    #
    # def get_success_url(self):
    #     # go back to where you came from (same pattern as create)
    #     nxt = self.request.GET.get("next") or self.request.POST.get("next")
    #     return nxt if nxt and nxt.startswith("/") and not nxt.startswith("//") else str(self.fallback_url)
    #
    # def form_valid(self, form):
    #     # If you add any custom logic here, you MUST return the super response
    #     return super().form_valid(form)