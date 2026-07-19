from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.apis.models import API
from apps.apis.selectors import APIVersionSelector
from apps.apis.serializers import APIVersionSerializer
from apps.apis.services import APIVersionService


class APIVersionListCreateView(generics.ListCreateAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_queryset(self):
        api = self.get_api()
        return APIVersionSelector.list_versions(api)

    def perform_create(self, serializer):
        api = self.get_api()

        APIVersionService.create_version(
            api=api,
            **serializer.validated_data,
        )

class APIVersionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version) 
    
    def perform_update(self, serializer):
        version = self.get_object()

        APIVersionService.update_version(
            version=version,
            **serializer.validated_data,
        )

class APIVersionDefaultView(generics.UpdateAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)

    def perform_update(self, serializer):
        api = self.get_api()
        version = self.get_object()

        APIVersionService.set_default_version(
            api=api,
            version=version,
        )          

class APIVersionActivateView(generics.UpdateAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)

    def perform_update(self, serializer):
        api = self.get_api()
        version = self.get_object()

        APIVersionService.activate_version(
            api=api,
            version=version,
        )        

class APIVersionDeactivateView(generics.UpdateAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)

    def perform_update(self, serializer):
        api = self.get_api()
        version = self.get_object()

        APIVersionService.deactivate_version(
            api=api,
            version=version,
        )        

class APIVersionDeleteView(generics.DestroyAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)

    def perform_destroy(self, instance):
     APIVersionService.delete_version(
        api=instance.api,
        version=instance,
    )
     

class APIVersionDetailView(generics.RetrieveAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)
    
class APIVersionUpdateView(generics.UpdateAPIView):
    serializer_class = APIVersionSerializer
    permission_classes = [IsAuthenticated]

    def get_api(self):
        return generics.get_object_or_404(
            API,
            id=self.kwargs["api_id"],
            is_active=True,
        )

    def get_object(self):
        api = self.get_api()
        version = self.kwargs["version"]
        return APIVersionSelector.get_version(api, version)    
