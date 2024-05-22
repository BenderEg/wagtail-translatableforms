import ast
import contextlib
import inspect

from django.apps import apps

from . import get_translatableform_model

def get_translation_source_content():
    translation_source_model = apps.get_model(
        app_label="wagtail_localize",
        model_name="translationsource",
    )
    return translation_source_model.objects.all().values_list(
        "content_json",
        flat=True,
    )

def get_unique_fields_names():
    model = get_translatableform_model()
    classes = inspect.getmro(model)
    fields = set()
    for class_ in classes[::-1]:
        with contextlib.suppress(TypeError):
            class_source = inspect.getsource(class_)
            class_node = ast.parse(class_source)
            for node in class_node.body[0].body:
                if not isinstance(node, ast.Assign):
                    continue
                if len(node.targets) != 1:
                    continue
                if not isinstance(node.targets[0], ast.Name):
                    continue
                if "keyword('unique', Constant(True))" in ast.dump(node.value, False):
                    fields.add(node.targets[0].id)
    return fields