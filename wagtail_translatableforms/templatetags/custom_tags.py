import datetime

from django.contrib.admin.templatetags.admin_list import result_headers, ResultList
from django.contrib.admin.utils import (
    display_for_field,
    display_for_value,
    lookup_field,
)
from django.db import models
from django.forms.utils import flatatt
from django.utils.encoding import force_str
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library
from wagtail.contrib.modeladmin.templatetags.modeladmin_tags import results
from wagtail.snippets.models import SnippetAdminURLFinder

from .. import get_translatableform_model

register = Library()


def items_for_result(view, result, request):
    """
    Generates the actual list of data.
    """
    modeladmin = view.model_admin
    url_finder_class = type(
            "_SnippetAdminURLFinder",
            (SnippetAdminURLFinder,),
            {"model": get_translatableform_model()}
        )
    url_finder = url_finder_class(request.user)
    for field_name in view.list_display:
        empty_value_display = modeladmin.get_empty_value_display(field_name)
        row_classes = ["field-%s" % field_name, "title"]
        try:
            f, attr, value = lookup_field(field_name, result, modeladmin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(
                attr, "empty_value_display", empty_value_display
            )
            if f is None or f.auto_created:
                allow_tags = getattr(attr, "allow_tags", False)
                boolean = getattr(attr, "boolean", False)
                if boolean or not value:
                    allow_tags = True
                result_repr = display_for_value(value, empty_value_display, boolean)

                # Strip HTML tags in the resulting text, except if the
                # function has an "allow_tags" attribute set to True.
                if allow_tags:
                    result_repr = mark_safe(result_repr)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(value, f, empty_value_display)

                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")
        if force_str(result_repr) == "":
            result_repr = mark_safe("&nbsp;")
        row_classes.extend(
            modeladmin.get_extra_class_names_for_field_col(result, field_name)
        )
        row_attrs = modeladmin.get_extra_attrs_for_field_col(result, field_name)
        row_attrs["class"] = " ".join(row_classes)
        row_attrs_flat = flatatt(row_attrs)
        primary_button = None
        if field_name == modeladmin.get_list_display_add_buttons(request):
            primary_button = view.button_helper.get_primary_button(result)
        if primary_button is not None and primary_button.get("url"):
            yield format_html(
                '<td{}><div class="title-wrapper"><a href="{}" title="{}">{}</a></div></td>',
                row_attrs_flat,
                url_finder.get_edit_url(result),
                primary_button.get("title", ""),
                result_repr,
            )
        else:
            yield format_html("<td{}>{}</td>", row_attrs_flat, result_repr)


def results(view, object_list, request):
    for item in object_list:
        yield ResultList(None, items_for_result(view, item, request))


@register.inclusion_tag("customforms/result_list.html", takes_context=True)
def custom_result_list(context):
    """
    Displays the headers and data list together
    """
    view = context["view"]
    object_list = context["object_list"]
    headers = list(result_headers(view))
    num_sorted_fields = 0
    for h in headers:
        if h["sortable"] and h["sorted"]:
            num_sorted_fields += 1
    context.update(
        {
            "result_headers": headers,
            "num_sorted_fields": num_sorted_fields,
            "results": list(results(view, object_list, context["request"])),
        }
    )
    return context