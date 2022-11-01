from rest_framework import generics

from custom_auth.api.serializers import ProfileSerializer
from custom_auth.models import Profile


class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = "email"
