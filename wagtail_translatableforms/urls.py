from django.urls import path

from .views import CustomSubmissionListView, CustomSubmissionDeleteView

urlpatterns = [
    path(
        "<int:pk>/submissions/",
        CustomSubmissionListView.as_view(),
        name="streamforms_submissions",
    ),
    path(
        "<int:pk>/submissions/delete/",
        CustomSubmissionDeleteView.as_view(),
        name="streamforms_delete_submissions",
    ),
]
