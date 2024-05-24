import environ

env = environ.Env()

SECRET_KEY = "secret"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "django.contrib.messages",
    # third party apps
    'rest_framework',
    'drf_spectacular',
    # wagtail
    "wagtail",
    "taggit",
    "wagtail.admin",
    "wagtail.snippets",
    "wagtail.users",
    "wagtail.contrib.forms",
    "wagtail.sites",
    "wagtail_modeladmin",
    'wagtail_localize',
    "wagtailstreamforms",
    "wagtail_translatableforms",
    "tests",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]


DATABASES = {
    "default": env.db("DATABASE_URL"),
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
            ]
        },
    }
]

ROOT_URLCONF = "tests.urls"

STATIC_URL = "/static/"

WAGTAILADMIN_BASE_URL = "https://127.0.0.1/cms/"
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", "English"),
    ("fr", "French"),
]
WAGTAIL_I18N_ENABLED = True
WAGTAIL_TRANSLATABLEFORM_SHOW_IP = True