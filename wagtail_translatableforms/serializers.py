from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from wagtailstreamforms.utils.general import get_slug_from_string

from . import get_translatableform_model
from .models import CustomFormSubmission


class FrieldsDataSerializer(serializers.Serializer):
    slug = serializers.CharField()
    type = serializers.CharField()
    label = serializers.CharField()
    required = serializers.BooleanField()
    help_text = serializers.CharField()
    default_value = serializers.CharField()


class TranslatableFormSerializer(serializers.ModelSerializer):
    fields_data = serializers.SerializerMethodField()

    class Meta:
        model = get_translatableform_model()
        fields = (
            "id",
            "title",
            "slug",
            "fields_data",
            "submit_button_text",
            "success_message",
            "error_message",
            "post_redirect_page",
            "process_form_submission_hooks",
        )
        read_only_fields = fields

    @extend_schema_field(field=FrieldsDataSerializer(many=True))
    def get_fields_data(self, obj):
        fields_data = [
            {"type": ele["type"], **ele["value"]} for ele in list(obj.fields.raw_data)
        ]
        return [
            {"slug": get_slug_from_string(ele["label"]), **ele} for ele in fields_data
        ]


class TranslatableFormSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomFormSubmission
        fields = ("form_id",)


def serialize_form(form_pk, serializer=TranslatableFormSerializer):
    if form_pk:
        form_instance = get_translatableform_model().objects.get(pk=form_pk)
        form_serializer = serializer(form_instance)
        return form_serializer.data