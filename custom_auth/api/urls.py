from django.urls import path

from custom_auth.api.views import ProfileDetail

urlpatterns = [
	# no list view, only detail view
    path("<str:email>", ProfileDetail.as_view(), name="user-detail"),
]
