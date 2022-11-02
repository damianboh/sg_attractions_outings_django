from django.shortcuts import redirect
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from attractions.api import permissions


from attractions.api.serializers import (
    AttractionSerializer,
    OutingSerializer,
    OutingInvitationSerializer,
    TagSerializer,
    AttractionSearchSerializer,
    OutingInvitationCreationSerializer,
    OutingCreateSerializer,
)
from attractions.models import Attraction, Outing, OutingInvitation, Tag
from attractions.tourism_hub_integrated import fill_attraction_details, search_and_save


class AttractionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Attraction.objects.all()
    serializer_class = AttractionSerializer
    fields = ["tags"] # using django-filter

    def get_object(self):
        attraction = super().get_object()
		# attraction might not have all details filled in yet
		# recall that details only filled in when user wants to see its details
        fill_attraction_details(attraction)
        return attraction
	
    @action(methods=["get"], detail=False)
    def search(self, request):
        search_serializer = AttractionSearchSerializer(data=request.GET)

        if not search_serializer.is_valid():
            return Response(search_serializer.errors)

        term = search_serializer.data["term"]

        search_and_save(term)

        attractions = self.get_queryset().filter(title__icontains=term)

        page = self.paginate_queryset(attractions)

        if page is not None:
            serializer = AttractionSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)
		
		# return original response if pagination returns nothing
        return Response(
            AttractionSerializer(attractions, many=True, context={"request": request}).data
        )


class OutingViewSet(viewsets.ModelViewSet):
    queryset = Outing.objects.all()
    permission_classes = [IsAuthenticated & permissions.IsCreatorPermission]

    def get_serializer_class(self):
		# if creating, use different serializer than when showing
        if self.request.method == "POST" or self.action == "create":
            return OutingCreateSerializer

        return OutingSerializer

    def get_object(self):
        outing = super(OutingViewSet, self).get_object()
        if (
            outing.creator != self.request.user.profile
            and outing.invites.filter(invitee=self.request.user.profile).count() == 0
        ):
            raise PermissionDenied()
        return outing

    def get_queryset(self):
        if self.action == "list":
            return self.queryset.filter(creator=self.request.user.profile)
        return super(OutingViewSet, self).get_queryset()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user.profile)
	
	# return all invited outings using /invited/
    @action(detail=False)
    def invited(self, request):
        outings = Outing.objects.filter(
            invites__in=OutingInvitation.objects.filter(invitee=request.user.profile)
        )

        page = self.paginate_queryset(outings)

        if page is not None:
            serializer = OutingSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        return Response(
            OutingSerializer(
                outings, many=True, context={"request": request}
            ).data
        )

    @action(methods=["post"], detail=True)
    def invite(self, request, pk):
        outing = self.get_object()
        if outing.creator != self.request.user.profile:
            raise PermissionDenied()

        serializer = OutingInvitationCreationSerializer(
            outing, data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors)

        serializer.save()
        return redirect("outing_detail", (outing.pk,))


class OutingInvitationViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OutingInvitationSerializer
    permission_classes = [IsAuthenticated & permissions.IsInviteePermission]



    def get_queryset(self):
        return OutingInvitation.objects.filter(invitee=self.request.user.profile)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
