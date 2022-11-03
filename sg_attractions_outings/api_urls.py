from django.urls import path, include
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# for swagger UI
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
import os

schema_view = get_schema_view(
	openapi.Info(
		title="Singapore Attractions Outings API",
		default_version="v1",
		description="API for Singapore Attractions Outings",
		),
		public=True,
)

urlpatterns = [
	# authentication
    path("auth/", include("rest_framework.urls")), # login page for DRF
    path("token-auth/", views.obtain_auth_token), # to get token for token authentication, stored in database
    path("jwt/", TokenObtainPairView.as_view(), name="jwt_obtain_pair"), # to get JWT token
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt_refresh"),
	
	# swagger UI
	path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui",),
		
	# API
    path("profiles/", include("custom_auth.api.urls")), # all APIs for getting user profiles info
    path("attractions/", include("attractions.api.urls")), # all APIs for getting attractions and outings info
]

# add to settings
SWAGGER_SETTINGS = {
	"SECURITY_DEFINITIONS": {
		"Token": {"type": "apiKey", "name": "Authorization",
		"in": "header"},
		"Basic": {"type": "basic"},
	}
}