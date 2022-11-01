from rest_framework import serializers

from custom_auth.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["name", "email", "about"]
