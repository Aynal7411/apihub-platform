from django.urls import path

from .views import ( RegistrationAPIView, LoginAPIView, RefreshTokenAPIView, CurrentUserAPIView,LogoutAPIView,
       LogoutAllAPIView,)
app_name = "accounts"

urlpatterns = [

    path(
        "auth/register/",
        RegistrationAPIView.as_view(),
        name="register",
    ),

    path(
        "auth/login/",
        LoginAPIView.as_view(),
        name="login",
    ),

    path(
        "auth/token/refresh/",
        RefreshTokenAPIView.as_view(),
        name="token-refresh",
    ),

     path(
        "auth/me/",
        CurrentUserAPIView.as_view(),
        name="me",
    ),
   path(
    "auth/logout/",
    LogoutAPIView.as_view(),
    name="logout",
),
   path(
        "auth/logout-all/",
        LogoutAllAPIView.as_view(),
        name="logout-all",
    ),

  

]