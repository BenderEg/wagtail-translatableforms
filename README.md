# WAGTAIL_TRANSLATABLEFORMS

Wagtail Translatableforms is an additional plagin for [Wagtail CMS](https://wagtail.org/).
It is based on [Wagtail Localize](https://pypi.org/project/wagtail-localize/), [Wagtailstreamforms](https://pypi.org/project/wagtailstreamforms/) and [Django](https://www.djangoproject.com/).

The main idea is to transform wagtailstreamform into translatable wagtail snippet and at the same time maintain wagtailstreamform fuctionality.

## Table of Contents

- Requirements
- Installation
- Usage
- License


## Requirements

* django = "^4.2.11";
* djangorestframework = ^3.15.0";
* drf_spectacular = "^0.27.1"
* wagtailstreamforms = "^4.1.0"
* wagtail-localize = "^1.8.2"
* wagtail = "^5.2.3"

## Installation

1. Install using pip:

```
pip install wagtail_translatableforms
```

2. Add 'wagtail_translatableforms' to your INSTALLED_APPS setting (make sure in goes after:
    'django.contrib.admin',
    'rest_framework',
    'drf_spectacular',
    'wagtail_modeladmin',
    'wagtail.snippets',
    'wagtail',
    'wagtail_localize',
    'wagtailstreamforms'
):

```
INSTALLED_APPS = [
    # ...
    "wagtail_translatableforms",
    # ...
]
```

## Usage

1. To use translatable form in your project import 'TranslatableFormBlock':

```
from wagtail_translatableforms.blocks import TranslatableFormBlock
```

2. To make api_represantation if using 'TranslatableFormBlock' in your custom StructBlocks you can import function 'serialize_form' and pass translatableform instance pk and optional a serializer.

```
from wagtail_translatableforms.serializers import serialize_form
```

3. To customize translatableform serializer you can import 'TranslatableFormSerializer' and subclass it:

```
from wagtail_translatableforms.serializers import TranslatableFormSerializer
```

4. To customize translatableform import and subclass 'AbstractTranslatableForm':

```
from wagtail_translatableforms.models import AbstractTranslatableForm
```

use 'get_translatableform_model' and 'get_translatableform_model_string' to reference model.

```
from wagtail_translatableforms import get_translatableform_model, get_translatableform_model_string
```

5. Settings.

* WAGTAIL_TRANSLATABLEFORM_FORM_MODEL = 'app.Model' (pass variable only in case of subclassing 'AbstractTranslatableForm');
* WAGTAIL_TRANSLATABLEFORM_SHOW_IP = True/False (add client IP in forms submissions representation, get IP from request.headers["X-Real-Ip"]. Pass Django Request object to 'process_form_submission' in your code. Default to False).

## License
This project is licensed under the [MIT License](https://github.com/BenderEg/wagtail-translatableforms/blob/main/LICENSE).
