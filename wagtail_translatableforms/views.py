from django.contrib.admin.utils import quote
from django.urls import reverse
from wagtail.contrib.modeladmin.helpers import AdminURLHelper
from wagtail.contrib.modeladmin.helpers import ButtonHelper
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import (
    SnippetViewSet,
    DeleteView,
)
from wagtailstreamforms.views import SubmissionListView, SubmissionDeleteView
from wagtailstreamforms.wagtail_hooks import FormModelAdmin

from . import get_translatableform_model


class CustomFormURLHelper(AdminURLHelper):
    def get_action_url(self, action, *args, **kwargs):

        if action == "submissions":
            return reverse(
                "wagtail_translatableforms:streamforms_%s" % action, args=args, kwargs=kwargs
            )

        if action == "edit":
            return reverse(
                get_translatableform_model().snippet_viewset.get_url_name("edit"),
                args=[quote(args[0])],
            )

        if action == "delete":
            return reverse(
                get_translatableform_model().snippet_viewset.get_url_name("delete"),
                args=[quote(quote(args[0]))],
            )

        if action == "create":
            return reverse(
                f"{get_translatableform_model().snippet_viewset.get_admin_url_namespace()}:list",
            )

        return super().get_action_url(action, *args, **kwargs)


class CustomFormButtonHelper(ButtonHelper):
    def button(self, pk, action, label, title, classnames_add, classnames_exclude):
        cn = self.finalise_classname(classnames_add, classnames_exclude)
        button = {
            "url": self.url_helper.get_action_url(action, quote(pk)),
            "label": label,
            "classname": cn,
            "title": title,
        }
        return button

    def get_buttons_for_obj(
        self, obj, exclude=None, classnames_add=None, classnames_exclude=None
    ):
        buttons = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        pk = getattr(obj, self.opts.pk.attname)
        buttons.append(
            self.button(
                pk,
                "submissions",
                "Submissions",
                "Submissions of this form",
                classnames_add,
                classnames_exclude,
            ),
        )
        return buttons

    def add_button(self, classnames_add=None, classnames_exclude=None):
        result = super().add_button(classnames_add, classnames_exclude)
        result["label"] = "Go to forms"
        result["title"] = f"Go to {self.verbose_name} creation menu"
        return result


@modeladmin_register
class CustomFormModelAdmin(FormModelAdmin):
    model = get_translatableform_model()
    menu_label = "Forms submitions"
    menu_order = 300
    button_helper_class = CustomFormButtonHelper
    url_helper_class = CustomFormURLHelper
    index_template_name = "customforms/index.html"


class CustomSubmissionListView(SubmissionListView):
    template_name = "customforms/index_submissions.html"
    model = get_translatableform_model()


class CustomSubmissionDeleteView(SubmissionDeleteView):
    model = get_translatableform_model()
    template_name = "customforms/confirm_delete.html"

    def get_success_url(self):
        return reverse(
            "wagtail_translatableforms:streamforms_submissions",
            kwargs={"pk": self.object.pk}
            )


class CustomDeleteView(DeleteView):

    def get_success_url(self):
        if "wagtail_translatableforms" in self.request.META.get("HTTP_REFERER"):
            return reverse(
                "wagtail_translatableforms_translatableform_modeladmin_index"
                )
        return super().get_success_url()


class TranslatableFromViewSet(SnippetViewSet):
    model = get_translatableform_model()
    icon = "form"
    menu_label = "Forms"
    menu_name = "Translatable forms"
    menu_order = 300
    add_to_admin_menu = True
    delete_view_class = CustomDeleteView


register_snippet(TranslatableFromViewSet)
