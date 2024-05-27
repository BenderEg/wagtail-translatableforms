from django.apps import AppConfig


class StreamsConfig(AppConfig):
    name = "wagtail_translatableforms"

    def ready(self) -> None:

        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured

        for app in (
            'django.contrib.admin',
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sites',
            'django.contrib.messages',
            'rest_framework',
            'drf_spectacular',
            'wagtail_modeladmin',
            'wagtail.snippets',
            'wagtail',
            'wagtail_localize',
            'wagtailstreamforms',
            ):
            if app not in settings.INSTALLED_APPS:
                raise ImproperlyConfigured(
                    f"""{app} must be in installed apps in suggested order before 'wagtail_translatableforms'.
                    Make sure 'wagtail_translatableforms' goes after:
                            'django.contrib.admin',
                            'rest_framework',
                            'drf_spectacular',
                            'wagtail_modeladmin',
                            'wagtail.snippets',
                            'wagtail',
                            'wagtail_localize',
                            'wagtailstreamforms',
                """)

        super().ready()

        from json import dumps, loads

        from django.db import transaction
        from django.template.defaultfilters import pluralize
        from django.urls import include, path
        from wagtail import hooks
        from wagtailstreamforms.hooks import register
        from wagtailstreamforms.serializers import FormSubmissionSerializer

        from . import get_translatableform_model
        from .models import CustomFormSubmissionFile
        from .urls import urlpatterns
        from .utils import get_translation_source_content


        @register('process_form_submission')
        def save_customform_submission_data(instance, form, request):
            """ saves the form submission data """

            # copy the cleaned_data so we dont mess with the original
            submission_data = form.cleaned_data.copy()
            submission_data["IP"] = request.headers.get("X-Real-Ip", "-")
            # change the submission data to a count of the files
            for field in form.files.keys():
                count = len(form.files.getlist(field))
                submission_data[field] = '{} file{}'.format(count, pluralize(count))

            # save the submission data
            submission = instance.get_submission_class().objects.create(
                form_data=dumps(submission_data, cls=FormSubmissionSerializer),
                form=instance
            )

            # save the form files
            for field in form.files:
                for file in form.files.getlist(field):
                    CustomFormSubmissionFile.objects.create(
                        submission=submission,
                        field=field,
                        file=file
                    )

        @hooks.register("register_admin_urls")
        def register_admin_urls():
            return [path("wagtail_translatableforms/",
                         include((urlpatterns, "wagtail_translatableforms"),
                    ))]


        @hooks.register("construct_main_menu")
        def remove_streamform_menu_item(request, menu_items):
            menu_items[:] = list(
                filter(
                    lambda x: x.name
                    != settings.WAGTAILSTREAMFORMS_ADMIN_MENU_LABEL.lower(),
                    menu_items,
                ),
            )

        @hooks.register("before_delete_snippet")
        def delete_related_translatebleform(request, instances):
            if request.method == "POST":
                content = get_translation_source_content()
                for instance in instances:
                    if isinstance(instance, get_translatableform_model()):
                        filtered = list(
                            filter(
                                lambda x: (tmp := loads(x))["pk"] == instance.pk
                                and tmp["translation_key"]
                                == str(instance.translation_key),
                                content,
                            ),
                        )
                        if filtered:
                            related_snippets = instance.__class__.objects.filter(
                                translation_key=instance.translation_key,
                            )
                            with transaction.atomic():
                                for ele in related_snippets:
                                    ele.delete()