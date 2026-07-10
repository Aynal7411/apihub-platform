from django.urls import path

from .views import RegistrationAPIView

urlpatterns = [

    path(
        "auth/register/",
        RegistrationAPIView.as_view(),
        name="register",
    ),

]