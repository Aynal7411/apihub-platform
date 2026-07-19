from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.apis.models import API, APIVersion
from apps.apis.serializers import APIEndpointSerializer
from apps.apis.selectors import APIEndpointSelector
from apps.apis.services import APIEndpointService



class APIEndpointListCreateView(generics.ListCreateAPIView):
    """
    List all endpoints of an API version
    Create a new endpoint
    """

    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_version(self):
        api = self.get_api()

        return get_object_or_404(
            APIVersion,
            api=api,
            version=self.kwargs["version"],
            is_active=True,
        )

    def get_queryset(self):
        version = self.get_version()

        return APIEndpointSelector.list_endpoints(version)

    def perform_create(self, serializer):
        version = self.get_version()

        serializer.instance = APIEndpointService.create_endpoint(
            version=version,
            **serializer.validated_data,
        )

class APIEndpointRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an endpoint
    """

    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_version(self):
        api = self.get_api()

        return get_object_or_404(
            APIVersion,
            api=api,
            version=self.kwargs["version"],
            is_active=True,
        )

    def get_object(self):
        version = self.get_version()
        endpoint_id = self.kwargs["endpoint_id"]

        return APIEndpointSelector.get_endpoint(endpoint_id)

    def perform_update(self, serializer):
        endpoint = self.get_object()

        serializer.instance = APIEndpointService.update_endpoint(
            endpoint=endpoint,
            **serializer.validated_data,
        )    

class APIEndpointUpdateView(generics.UpdateAPIView):  
    
    """
    Update an endpoint
    """

    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_version(self):
        api = self.get_api()

        return get_object_or_404(
            APIVersion,
            api=api,
            version=self.kwargs["version"],
            is_active=True,
        )

    def get_object(self):
        version = self.get_version()
        endpoint_id = self.kwargs["endpoint_id"]

        return APIEndpointSelector.get_endpoint(endpoint_id)

    def perform_update(self, serializer):
        endpoint = self.get_object()

        serializer.instance = APIEndpointService.update_endpoint(
            endpoint=endpoint,
            **serializer.validated_data,
        )    

class APIEndpointDeleteView(generics.DestroyAPIView):
    """
    Delete an endpoint
    """

    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_version(self):
        api = self.get_api()

        return get_object_or_404(
            APIVersion,
            api=api,
            version=self.kwargs["version"],
            is_active=True,
        )

    def get_object(self):
        version = self.get_version()
        endpoint_id = self.kwargs["endpoint_id"]

        return APIEndpointSelector.get_endpoint(endpoint_id)

    def perform_destroy(self, instance):
        instance.delete()              