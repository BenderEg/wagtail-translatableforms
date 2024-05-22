from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailstreamforms.blocks import WagtailFormBlock

from . import get_translatableform_model
from .serializers import TranslatableFormSerializer


class TranslatableFormBlock(WagtailFormBlock):
    form = SnippetChooserBlock(target_model=get_translatableform_model())
    form_title = blocks.TextBlock(max_length=255, required=False)
    form_text = blocks.TextBlock(required=False)
    form_action = None

    def clean(self, value):
        result = super().clean(value)
        if not any((result.get("form_title"), result.get("form_text"))):
            msg = """Either "form title" or "form text" must be specified"""
            raise blocks.StructBlockValidationError(
                block_errors={
                    "form_title": ValidationError(msg),
                    "form_text": ValidationError(msg),
                },
            )
        return result

    def get_api_representation(self, value, context=None):
        representation = self.get_prep_value(value)
        form_pk = representation.get("form")
        if form_pk:
            form_instance = get_translatableform_model().objects.get(pk=form_pk)
            form_serializer = TranslatableFormSerializer(form_instance)
            representation["form"] = form_serializer.data
        return representation

    class Meta:
        icon = "form"