from django.urls import include, path
from rest_framework.routers import DefaultRouter

from attractions.api.views import (
    AttractionViewSet,
    OutingViewSet,
    OutingInvitationViewSet,
    TagViewSet,
)

router = DefaultRouter()
router.register("attractions", AttractionViewSet)
router.register("outings", OutingViewSet, basename="outing")
router.register("outing_invitations", OutingInvitationViewSet, basename="outinginvitation")
router.register("tags", TagViewSet)

urlpatterns = [path("", include(router.urls))]
