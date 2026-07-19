from django.urls import path

from apps.apis.views import (
    APIListCreateView,
    APIRetrieveView,
    APIUpdateView,
    APIDeleteView,
)

from apps.apis.views import (
    APIVersionListCreateView,
    APIVersionRetrieveUpdateDestroyView,
   
    APIVersionDeleteView,
    APIVersionDefaultView,
    APIVersionActivateView,
    APIVersionDeactivateView,
    APIVersionDetailView,
    APIVersionUpdateView,
)

from apps.apis.views import (
    APIEndpointListCreateView,
    APIEndpointRetrieveUpdateDestroyView,
    APIEndpointUpdateView,
    APIEndpointDeleteView
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

     path(
        "<uuid:api_id>/versions/",APIVersionListCreateView.as_view(), name="api-version-list-create"),

     path(
        "<uuid:api_id>/versions/<str:version>/",APIVersionRetrieveUpdateDestroyView.as_view(), name="api-version-detail"),

      path(
        "<uuid:api_id>/versions/<str:version>/update/",APIVersionUpdateView.as_view(), name="api-version-update"),

      path("<uuid:api_id>/versions/<str:version>/delete/",APIVersionDeleteView.as_view(), name="api-version-delete"),

      path("<uuid:api_id>/versions/<str:version>/default/", APIVersionDefaultView.as_view(), name="api-version-default"),

      path("<uuid:api_id>/versions/<str:version>/activate/", APIVersionActivateView.as_view(), name="api-version-activate"),
      path("<uuid:api_id>/versions/<str:version>/deactivate/", APIVersionDeactivateView.as_view(), name="api-version-deactivate"),
      path("<uuid:api_id>/versions/<str:version>/detail/", APIVersionDetailView.as_view(), name="api-version-detail-view"),

    # API Endpoint URLs
    path(
        "<uuid:api_id>/versions/<str:version>/endpoints/",
        APIEndpointListCreateView.as_view(),
        name="api-endpoint-list-create",
    ),
    path(
        "<uuid:api_id>/versions/<str:version>/endpoints/<uuid:endpoint_id>/",
        APIEndpointRetrieveUpdateDestroyView.as_view(),
        name="api-endpoint-detail",
    ),
    path(
        "<uuid:api_id>/versions/<str:version>/endpoints/<uuid:endpoint_id>/update/",
        APIEndpointUpdateView.as_view(),
        name="api-endpoint-update",
    ),
    path(
        "<uuid:api_id>/versions/<str:version>/endpoints/<uuid:endpoint_id>/delete/",
        APIEndpointDeleteView.as_view(),
        name="api-endpoint-delete",
    ),


]