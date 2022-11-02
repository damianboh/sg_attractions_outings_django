from rest_framework import serializers

from custom_auth.models import Profile
from attractions.models import Attraction, Outing, OutingInvitation, Tag


# to allow creation of new Tags when Attraction instance is created, to use in AttrationSerializer
class TagField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(name=data)[0]
        except (TypeError, ValueError):
            self.fail(f"Tag value {data} is invalid")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class AttractionSerializer(serializers.ModelSerializer):
	# to allow creation of new Tag when Attraction instance is created
    tag = TagField(slug_field="name", many=True, read_only=True)

    class Meta:
        model = Attraction
        fields = "__all__"
        read_only_fields = [
			"uuid",
            "name",
			"attraction_type",
            "summary",
            "full_description",
            "imdb_id",
            "nearest_station",
			"website_url",
			"admission_info",
			"map_url",
			"saved_by",
            "is_full_record",
		]


# to display inside outing to show which attraction the outing is for
class AttractionNameAndUrlSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField("outing_detail", read_only=True)

    class Meta:
        model = Attraction
        fields = ["name", "url"]


class OutingInvitationSerializer(serializers.ModelSerializer):
	# invitee will be shown as url link
    invitee = serializers.HyperlinkedRelatedField(
        "profile_detail", read_only=True, lookup_field="email"
    )

    class Meta:
        model = OutingInvitation
        fields = "__all__"
        read_only_fields = ["attendance_confirmed", "outing", "invitee"]


# need to validate_invitee before creation, invitee might have been already invited
class OutingInvitationCreationSerializer(serializers.ModelSerializer):
    invitee = serializers.HyperlinkedRelatedField(
        "profile_detail", queryset=Profile.objects.all(), lookup_field="email"
    )

    class Meta:
        model = OutingInvitation
        fields = ["invitee"]

    def __init__(self, outing, *args, **kwargs):
        self.outing = outing
        super(OutingInvitationCreationSerializer, self).__init__(*args, **kwargs)

    def save(self, **kwargs):
        kwargs["outing"] = self.outing
        return super(OutingInvitationCreationSerializer, self).save(**kwargs)

    def validate_invitee(self, invitee):
        existing_invitation = OutingInvitation.objects.filter(
            invitee=invitee, outing=self.outing
        ).first()
        if existing_invitation:
            raise serializers.ValidationError(
                f"{invitee.email} has already been invited to this outing."
            )
        return invitee


class OutingSerializer(serializers.ModelSerializer):
    attraction = AttractionNameAndUrlSerializer(read_only=True)
    creator = serializers.HyperlinkedRelatedField(
        "profile_detail", read_only=True, lookup_field="email"
    )
    invites = OutingInvitationSerializer(read_only=True, many=True)

    class Meta:
        model = Outing
        fields = "__all__"
        read_only_fields = ["attraction", "creator", "start_notification_sent", "invites"]


# different from above, override attraction
# when creating outing, just use url
# when viewing outing, view attraction name and url together
class OutingCreateSerializer(OutingSerializer):
    attraction = serializers.HyperlinkedRelatedField(
        view_name="outing_detail", queryset=Attraction.objects.all()
    )

    class Meta(OutingSerializer.Meta):
        read_only_fields = ["start_notification_sent", "invites"]


class AttractionSearchSerializer(serializers.Serializer):
    term = serializers.CharField()
