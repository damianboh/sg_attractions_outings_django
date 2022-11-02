from rest_framework import generics

from custom_auth.api.serializers import ProfileSerializer
from custom_auth.models import Profile
from rest_framework.permissions import IsAuthenticated


class ProfileDetail(generics.RetrieveAPIView): # no list view, only detail view for each profile
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = "email"
    permission_classes = [IsAuthenticated]
