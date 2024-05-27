from json import loads
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete
from wagtail.models import TranslatableMixin
from wagtail_localize.models import TranslationSource
from wagtailstreamforms import hooks
from wagtailstreamforms.models.form import AbstractForm
from wagtailstreamforms.utils.loading import get_advanced_settings_model

from . import get_translatableform_model_string, get_translatableform_model
from .utils import get_translation_source_content, get_unique_fields_names


class CustomTranslatableMixin(TranslatableMixin):
    def get_translation(self, locale):
        try:
            return super().get_translation(locale)
        except self.DoesNotExist:
            obj_copy = self.copy_for_translation(locale)
            for field in get_unique_fields_names():
                value = getattr(obj_copy, field)
                if type(value) is not str:
                    continue
                setattr(obj_copy, field, f"{value}-{str(locale)}")
                obj_copy.save()
            return super().get_translation(locale)

    class Meta:
        abstract = True
        unique_together = [("translation_key", "locale")]


class CustomFormSubmission(models.Model):
    """Data for a form submission."""

    form_data = models.TextField("Form data")
    form = models.ForeignKey(
        get_translatableform_model_string(),
        verbose_name="TranslatableForm",
        on_delete=models.CASCADE,
    )
    submit_time = models.DateTimeField("Submit time", auto_now_add=True)

    def get_data(self):
        """Returns dict with form data."""
        form_data = loads(self.form_data)
        form_data.update({"submit_time": self.submit_time})
        return form_data

    def __str__(self):
        return self.form_data

    class Meta:
        ordering = ["-submit_time"]
        verbose_name = "Form submission"


class CustomFormSubmissionFile(models.Model):
    """Data for a form submission file."""

    submission = models.ForeignKey(
        "wagtail_translatableforms.CustomFormSubmission",
        verbose_name="Submission",
        on_delete=models.CASCADE,
        related_name="files",
    )
    field = models.CharField(verbose_name="Field", max_length=255)
    file = models.FileField(verbose_name="File", upload_to="streamforms/")

    def __str__(self):
        return self.file.name

    class Meta:
        ordering = ["field", "file"]
        verbose_name = "Form submission file"

    @property
    def url(self):
        return self.file.url


def delete_file_from_storage(instance, **kwargs):
    """Cleanup deleted files from disk"""
    transaction.on_commit(lambda: instance.file.delete(False))


post_delete.connect(delete_file_from_storage, sender=CustomFormSubmissionFile)


class AbstractTranslatableForm(CustomTranslatableMixin, AbstractForm):

    class Meta:
        abstract = True
        ordering = ["title"]
        unique_together = ("translation_key", "locale")

    def copy(self):
        """Copy this form and its fields."""

        form_copy = get_translatableform_model()(
            site=self.site,
            title=self.title,
            slug=uuid4(),
            template_name=self.template_name,
            fields=self.fields,
            submit_button_text=self.submit_button_text,
            success_message=self.success_message,
            error_message=self.error_message,
            post_redirect_page=self.post_redirect_page,
            process_form_submission_hooks=self.process_form_submission_hooks,
        )
        form_copy.save()

        # additionally copy the advanced settings if they exist
        SettingsModel = get_advanced_settings_model()

        if SettingsModel:
            try:
                advanced = SettingsModel.objects.get(form=self)
                advanced.pk = None
                advanced.form = form_copy
                advanced.save()
            except SettingsModel.DoesNotExist:
                pass

        return form_copy

    def get_submission_class(self):
        """Returns submission class."""
        return CustomFormSubmission

    @transaction.atomic()
    def delete(self, **kwargs) -> tuple[int, dict[str, int]]:
        content = get_translation_source_content()
        filtered = list(
            filter(
                lambda x: (tmp := loads(x))["pk"] == self.pk
                and tmp["translation_key"] == str(self.translation_key),
                content,
            ),
        )
        if filtered:
            related_forms = self.__class__.objects.exclude(pk=self.pk).filter(
                translation_key=self.translation_key,
            )
            with transaction.atomic():
                for ele in related_forms:
                    ele.delete()
        return super().delete(**kwargs)


    def process_form_submission(self, form, ip_addr=None):
        """Runs each hook if selected in the form."""

        for fn in hooks.get_hooks("process_form_submission"):
            if fn.__name__ in self.process_form_submission_hooks:
                fn(self, form, ip_addr)

    def get_data_fields(self):
        data_fields = super().get_data_fields()
        if getattr(settings, "WAGTAIL_TRANSLATABLEFORM_SHOW_IP", False):
            data_fields.append(("IP", "IP"))
        return data_fields

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        source = TranslationSource.objects.get_for_instance_or_none(self)
        if source:
            TranslationSource.update_or_create_from_instance(self)


class TranslatableForm(AbstractTranslatableForm):
    pass