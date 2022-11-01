from django.urls import path

from custom_auth.api.views import ProfileDetail

urlpatterns = [
    path("profiles/<str:email>", ProfileDetail.as_view(), name="user-detail"),
]
