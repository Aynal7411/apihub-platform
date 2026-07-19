from django.urls import path

from apps.apis.views import (
    APIListCreateView,
    APIRetrieveView,
    APIUpdateView,
    APIDeleteView,
)

urlpatterns = [
    path(
        "",
        APIListCreateView.as_view(),
        name="api-list-create",
    ),

    path(
        "<uuid:id>/",
        APIRetrieveView.as_view(),
        name="api-detail",
    ),

    path(
        "<uuid:id>/update/",
        APIUpdateView.as_view(),
        name="api-update",
    ),
    path(
        "<uuid:id>/delete/",
        APIDeleteView.as_view(),
        name="api-delete",
    ),
]