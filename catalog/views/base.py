from django.views.generic import TemplateView

from catalog.models import Work, BookSet


class CatalogBaseView(TemplateView):
    template_name = "catalog/work_list.html"

    def get_context_data(self, **kwargs):
        context = super(CatalogBaseView, self).get_context_data(**kwargs)
        view_type = getattr(self, "view_type", "all")

        if view_type == "works":
            context["items"] = Work.objects.all().order_by("sort_title")
            context["heading"] = "Works"
            context["sub_heading"] = ("Creative texts (novels, poems, essays, "
                                      "or stories) independent of any "
                                      "particular edition or printing.")
        elif view_type == "booksets":
            context["items"] = BookSet.objects.all().order_by("title")
            context["heading"] = "Book Sets"
            context["sub_heading"] = ("A group of volumes published or "
                                      "packaged as a unit. May or may not be "
                                      "'boxed.'")
        else:
            # Combine both - combine QuerySets to lists so they're concatenable
            items_list = list(Work.objects.all()) + list(BookSet.objects.all())
            items_sorted = sorted(items_list, key=lambda i: i.sort_title)
            context["items"] = items_sorted
            context["heading"] = "All Works and Book Sets"

        context["view_type"] = view_type
        return context
