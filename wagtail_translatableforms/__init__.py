from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

setattr(settings, "WAGTAILSTREAMFORMS_ADMIN_MENU_LABEL", "Deprecated")
setattr(settings, "WAGTAILSTREAMFORMS_ENABLE_BUILTIN_HOOKS", False)

def get_translatableform_model_string():
    return getattr(
        settings,
        "WAGTAIL_TRANSLATABLEFORM_FORM_MODEL",
        "wagtail_translatableforms.TranslatableForm",
        )

def get_translatableform_model():

    from django.apps import apps

    model_string = get_translatableform_model_string()
    try:
        return apps.get_model(model_string, require_ready=False)
    except ValueError:
        raise ImproperlyConfigured(
            "WAGTAIL_TRANSLATABLEFORM_FORM_MODEL must be of the form 'app_label.model_name'"
        )
    except LookupError:
        raise ImproperlyConfigured(
            "WAGTAIL_TRANSLATABLEFORM_FORM_MODEL refers to model '%s' that has not been installed"
            % model_string
        )
