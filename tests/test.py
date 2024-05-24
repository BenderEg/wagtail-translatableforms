import json

from django.apps import apps
from django.http import HttpRequest
from django.test import TestCase
from rest_framework.request import Request
from wagtail_localize.operations import translate_object
from wagtail_localize.models import (
    TranslationSource,
    Translation,
    StringSegment,
)
from wagtail_translatableforms import get_translatableform_model
from wagtail_translatableforms.models import CustomFormSubmission

from .exceptions import FormNotValidError

class TranslatableModelTestCase(TestCase):

    def setUp(self):
        self.create_model_instance()
        self.add_fr_locale()
        self.submit_form()
        self.translate_instance()

    def test_model_creation(self):
        self.assertEqual(
            self.get_model_instance().exists(), True
            )

    def test_new_locale(self):
        self.assertEqual(
            self.get_fr_locale_instance().exists(), True
        )

    def test_form_submission(self):
        form_submission = self.get_form_submission()
        form_data = json.loads(form_submission.form_data)
        self.assertEqual(form_data.get("IP"), "-")

    def test_translation(self):
        self.assertEqual(
            len(get_translatableform_model().objects.all()), 2
        )
        self.assertEqual(
            self.check_translation(), (False, True, 4)
        )

    def create_model_instance(self):
        en_locale = self.get_locale_model().objects.get(language_code="en")
        get_translatableform_model().objects.create(
            title="test",
            slug="test",
            template_name="streamforms/form_block.html",
            process_form_submission_hooks="save_customform_submission_data",
            locale=en_locale,
            fields=[
                {
                    "id": "1eb81919-7988-49d8-9681-4cd699eaf6cd",
                    "type": "singleline",
                    "value": {
                        "label": "name",
                        "required": False,
                        "help_text": "",
                        "default_value": ""
                    }
                }
                ]
            )

    def get_locale_model(self):
        return apps.get_model(app_label="wagtailcore", model_name="locale")

    def add_fr_locale(self):
        self.get_locale_model().objects.create(language_code="fr")

    def get_fr_locale_instance(self):
        return self.get_locale_model().objects.filter(language_code="fr")

    def get_model_instance(self):
        return get_translatableform_model().objects.filter(slug="test")

    def translate_instance(self):
        instance = self.get_model_instance().first()
        locale = self.get_fr_locale_instance().first()
        translate_object(
            instance,
            [locale,]
            )
        instance.get_translation(locale)

    def check_translation(self):
        instance = self.get_model_instance().first()
        source, source_created = TranslationSource.get_or_create_from_instance(instance)
        translation_exists = Translation.objects.filter(source=source).exists()
        string_segments_len = len(StringSegment.objects.filter(source=source))
        return source_created, translation_exists, string_segments_len


    def submit_form(self):
        instance = self.get_model_instance().first()
        data = {
            "name": "Alise",
            "form_id": str(instance.pk),
            "form_reference": "14002ec7-9efb-46ee-afef-ca9f075046877",
        }
        http_request = HttpRequest()
        request = Request(http_request)
        form = instance.get_form(data, request.FILES, user=request.user)
        if form.is_valid():
            instance.process_form_submission(form, request)
            return
        raise FormNotValidError("Form not valid!")

    def get_form_submission(self):
        instance = self.get_model_instance().first()
        return CustomFormSubmission.objects.get(form=instance)