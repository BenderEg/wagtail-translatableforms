from django.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls


urlpatterns = [
    path("cms/", include(wagtailadmin_urls)),
    path("", include(wagtail_urls)),
]

urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
)